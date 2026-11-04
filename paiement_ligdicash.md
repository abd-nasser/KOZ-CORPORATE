# Paiement LigdiCash — guide de bout en bout

Ce document explique le paiement LigdiCash du projet KOZ Services. La première partie est volontairement simple; la seconde donne à un développeur ou à l’agent Agy les détails nécessaires pour comprendre et modifier le flux sans casser sa sécurité.

## Explication simple

Imagine que le site est une boutique, et que LigdiCash est la caisse de la banque.

1. **Le client choisit une commande.** Le site vérifie que cette commande lui appartient, qu’elle est encore à payer et qu’elle contient des articles.
2. **Le client donne le numéro de son compte LigdiCash.** Le site vérifie qu’il contient huit chiffres, puis ajoute `226`, l’indicatif du Burkina Faso.
3. **Le client demande un code secret temporaire (OTP).** Le site demande à LigdiCash d’envoyer ce code au client. Le site ne fabrique pas le code et ne le connaît pas.
4. **Le client tape le code reçu.** Le site demande à LigdiCash de vérifier le code et de lancer le paiement. Si LigdiCash accepte la demande, le site garde le numéro de ticket (le `token`) et une référence unique pour retrouver le paiement.
5. **LigdiCash rappelle le site quand le paiement a avancé.** Ce rappel s’appelle un callback. Le site ne croit pas simplement le message reçu : il demande directement à LigdiCash si le paiement est vraiment terminé.
6. **Si LigdiCash confirme le bon montant**, le site marque le paiement et la commande comme payés et retire les articles du stock. Si le paiement attend encore, le site attend un autre callback.

Le code OTP est comme une clé à usage temporaire : il sert à prouver à LigdiCash que le client autorise le paiement. Le callback, lui, est comme un reçu que le site fait vérifier à la caisse avant de remettre la commande.

## Parcours technique

### 1. Afficher la page de paiement

- Vue : `page_paiement` dans `src/paiement_app/views.py`.
- URL : `/paiement/commande/<commande_id>/` (nom Django : `paiement_app:page-paiement`).
- Cette vue exige une connexion utilisateur et ne présente que sa propre commande.
- La commande doit être au statut `validee` et le panier ne doit pas être vide.
- Le formulaire est dans `src/templates/paiement_templates/paiement.html`.

### 2. Demander l’envoi de l’OTP

- Vue : `envoyer_otp`.
- URL : `/paiement/commande/<commande_id>/otp/` (nom : `paiement_app:envoyer-otp`).
- Méthode HTTP : `POST`, réservée au client connecté propriétaire de la commande.
- Le serveur vérifie le téléphone, le montant entier en XOF, les limites documentées par LigdiCash (10 à 2 000 000 FCFA) et l’absence d’un autre paiement en attente.
- Il appelle :

  ```text
  GET https://app.ligdicash.com/pay/v02/debitotp/{telephone_226}/{montant}
  ```

- Les identifiants sont envoyés dans les en-têtes `Apikey` et `Authorization: Bearer ...`.
- Le code n’est pas enregistré par le site. En cas de succès (`error: false`), la session ne garde que le hash SHA-256 du téléphone et le montant. Cela permet de vérifier lors de l’étape suivante que téléphone et commande n’ont pas changé.
- La réponse de succès fait apparaître le champ OTP dans la page. Le bouton « Renvoyer le code OTP » appelle la même étape.

### 3. Valider le code et envoyer le paiement

- Vue : `initier_paiement`.
- URL : `/paiement/commande/<commande_id>/initier/` (nom : `paiement_app:initier-paiement`).
- Méthode HTTP : `POST`, avec téléphone et OTP à six chiffres.
- Le serveur refait les validations de commande et de montant. Il compare le téléphone et le montant avec la demande d’OTP enregistrée dans la session.
- Le serveur construit le détail des articles puis envoie :

  ```text
  POST https://app.ligdicash.com/pay/v02/debitwallet/withotp
  ```

  Le JSON suit l’enveloppe LigdiCash `commande.invoice`, `commande.store`, `commande.actions` et `commande.custom_data`. La facture contient le numéro au format `226XXXXXXXX`, le montant entier, la devise `XOF`, les articles et l’OTP. `custom_data.transaction_id` contient une référence unique créée côté serveur.

- Si LigdiCash répond `response_code: "00"` avec un token, le site crée un `Paiement` au statut `en_attente`, stocke le token, le numéro et la référence, puis lie le paiement à la commande. La session OTP est supprimée.
- La réponse signifie seulement que la demande a été prise en compte : **elle ne signifie pas que le paiement est déjà confirmé**.

### 4. Recevoir et vérifier le callback

- Vue : `callback_ligdicash`.
- URL : `/paiement/callback/` (nom : `paiement_app:callback-ligdicash`), publique et exemptée du contrôle CSRF dans `src/paiement_app/urls.py` pour permettre l’appel par LigdiCash.
- La vue lit `transaction_id` depuis le tableau `custom_data` reçu, puis retrouve le paiement à partir de la référence sauvegardée. Le `token` fourni dans le callback n’est pas utilisé pour réconcilier la commande.
- La vue appelle le endpoint `confirm` avec **le token conservé lors de la création** :

  ```text
  GET https://app.ligdicash.com/pay/v01/redirect/checkout-invoice/confirm/?invoiceToken={token_en_base}
  ```

- Seule la réponse authentifiée de `confirm` fait foi :
  - `pending` : laisser le paiement en attente; LigdiCash peut rappeler plus tard.
  - `notcompleted` : marquer le paiement `echec`.
  - `completed` : vérifier que le montant confirmé correspond au montant enregistré.
  - autre réponse, erreur réseau ou montant non conforme : ne pas marquer la commande payée; répondre avec une erreur afin que le callback puisse être retenté.

### 5. Mettre à jour la commande et le stock

- Quand le statut est `completed` et que le montant correspond, une transaction de base de données verrouille le paiement et les produits concernés.
- Le paiement est marqué `paye`, la commande `payee` et les stocks sont diminués une seule fois. La vérification du statut en attente sous verrou empêche un callback répété de diminuer le stock une seconde fois.
- Une alerte est envoyée pour les produits dont le stock est inférieur ou égal à trois.
- **Cas à surveiller :** si le paiement est bien confirmé par LigdiCash mais que le stock est insuffisant, le code actuel journalise le problème, marque quand même le paiement et la commande comme payés, et ne diminue pas le stock. Il ne déclenche pas automatiquement de remboursement; ce cas doit être traité manuellement ou faire l’objet d’une évolution métier.

## Composants

| Fichier | Responsabilité |
|---|---|
| `src/paiement_app/views.py` | Validations, appels API, création du paiement et traitement du callback |
| `src/paiement_app/urls.py` | Routes des pages, demande OTP, paiement et callback |
| `src/paiement_app/models.py` | Enregistrement des paiements, statuts, token et références LigdiCash |
| `src/templates/paiement_templates/paiement.html` | Formulaire client et passage de la demande OTP à la confirmation |
| `src/koz_flow/settings.py` | Chargement des paramètres LigdiCash depuis l’environnement |

## Configuration et règles pour Agy

Variables nécessaires dans l’environnement du serveur (ne pas les écrire dans Git) :

```text
LIGDICASH_API_KEY=...
LIGDICASH_API_TOKEN=...
```

Règles à respecter lors de toute modification :

1. Ne jamais exposer `LIGDICASH_API_KEY` ou `LIGDICASH_API_TOKEN` au navigateur, dans les logs, ni dans un fichier versionné.
2. Ne jamais considérer le retour de `/debitotp` ou de `/debitwallet/withotp` comme une preuve de paiement final.
3. Ne jamais accepter le statut, le token ou le montant du callback comme source de vérité. Retrouver la transaction avec la référence personnalisée connue du serveur, puis appeler `confirm` avec le token sauvegardé.
4. Ne marquer la commande `payee` qu’après `confirm.status == "completed"` et vérification exacte du montant.
5. Conserver un traitement idempotent : un callback répété ne doit pas déduire le stock plusieurs fois.
6. Conserver la validation serveur de la commande, du numéro, du montant, de l’OTP et du code HTTP/API. Les contrôles HTML ou JavaScript ne suffisent pas.
7. Après une modification, vérifier la syntaxe Python, les routes, les deux appels HTTP et les scénarios callback `pending`, `notcompleted`, `completed`, montant incorrect et callback dupliqué. Utiliser des réponses HTTP simulées pour les tests; ne pas lancer de vrais débits en test.

## Limites fonctionnelles à connaître

- Le téléphone est actuellement limité au format burkinabè : huit chiffres locaux, préfixés par `226`.
- La page affiche « Paiement en cours de validation » après acceptation de la demande. L’utilisateur doit consulter le statut de sa commande; la redirection automatique de l’ancienne interface ne doit pas être réintroduite comme preuve de paiement.
- L’OTP est géré et expiré par LigdiCash. Le site conserve la preuve qu’une demande a été faite pour ce téléphone et ce montant, mais ne reçoit pas de durée d’expiration OTP de l’API dans ce flux.
- Pour la référence de l’intégration et les formats de réponse, consulter la documentation officielle :
  - [Wallet LigdiCash — OTP sans redirection](https://developers.ligdicash.com/api-paiement/payin-sans-redirect/operateurs/wallet-ligdicash)
  - [Vérifier le statut](https://developers.ligdicash.com/api-paiement/payin-sans-redirect/verifier-statut)
  - [Sécuriser le callback](https://developers.ligdicash.com/api-paiement/callback/securisation)
