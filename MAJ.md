# Mise a jour du formulaire de depot des documents

## Objectif

Adapter le depot des pieces de financement au profil du client sans maintenir deux formulaires ni creer une seconde vue. Le formulaire existant `DocumentsUploadForm` gere maintenant deux parcours : salarie et entrepreneur. Le parcours est determine par `client.profession_choisie` ; la valeur `entrepreneur` active le parcours entreprise.

## Modele `Documents`

Le modele `client_app.Documents` a ete complete avec les pieces entrepreneur qui n'existaient pas :

- `formulaire_kyc` : formulaire KYC renseigne et signe ;
- `consentement_bic` : formulaire de consentement BIC ;
- `extrait_rccm_ifu` : extrait RCCM et IFU ;
- `statuts_enregistres` : statuts enregistres ;
- `attestation_regularite_fiscale` : attestation de regularite ou situation fiscale ;
- `pieces_identite_signataires` : pieces d'identite de chaque signataire ;
- `pieces_beneficiaires_effectifs` : justificatifs d'identite et/ou RCCM des beneficiaires effectifs ;
- `cv_promoteur_gerant` : CV du promoteur ou du gerant ;
- `etats_financiers_1`, `etats_financiers_2`, `etats_financiers_3` : etats financiers certifies des trois derniers exercices ;
- `plan_affaires` : plan d'affaires sur la duree du pret.

Ces FileFields sont facultatifs dans le modele afin de ne pas rendre invalides les dossiers existants. Leur caractere obligatoire est applique dans le formulaire selon le profil. Les pieces multiples des signataires et beneficiaires sont collectees dans un fichier chacune ; le formulaire indique au client de les regrouper.

Les pieces deja presentes dans le modele sont reutilisees lorsqu'elles correspondent a la checklist : piece d'identite, justificatif de residence, releves bancaires et RIB, specimen de signature, fiche de demande, geolocalisation, garanties et recu d'acompte. Le libelle des releves bancaires indique 24 mois.

La facture proforma a ete ecartee a la demande du responsable produit. Elle n'est presente ni dans le modele final ni dans le formulaire. L'historique de migration conserve son ajout puis sa suppression.

## Formulaire dynamique

`DocumentsUploadForm` conserve un seul `ModelForm` et accepte maintenant le client avec l'argument `client`. Si cet argument n'est pas donne, le formulaire tente de recuperer le client depuis l'instance `Documents`.

Les champs obligatoires sont repartis en trois groupes :

- Communs : CNI/passeport, justificatif de domicile, releve bancaire et specimen de signature.
- Salarie : attestation de non-engagement, contrat et attestation de travail, trois bulletins de paie.
- Entrepreneur : KYC, consentement BIC, RCCM/IFU, statuts, situation fiscale, pieces des signataires et beneficiaires effectifs, CV du promoteur/gerant, trois etats financiers et plan d'affaires.

La fiche de demande, les garanties et le recu d'acompte restent facultatifs pour les deux profils et sont presentes dans la section « Autres justificatifs ».

Pour le profil entrepreneur, les champs lies a l'emploi salarie ne sont pas requis. Pour le parcours salarie, les champs entrepreneur ne sont pas requis. La verification des pieces manquantes reutilise les libelles des champs du formulaire ; les controles existants de taille, type MIME et extension restent en place.

## Completeness et sauvegarde

`Documents.verifier_completude()` applique la meme separation que le formulaire : pieces communes, puis liste salariale ou entrepreneur. La localisation est consideree complete si les deux coordonnees GPS sont presentes ou si le client fournit le plan papier de geolocalisation. Si les deux options sont absentes, le dossier reste incomplet. Une coordonnee GPS egale a zero est traitee comme valide.

Les vues de depot et de mise a jour fournissent le client au formulaire. Cela couvre le detail d'une demande, l'upload d'une demande, l'upload d'une offre, le detail/mise a jour d'un dossier et le detail d'une offre. Les vues existantes sont conservees ; aucune nouvelle vue n'a ete creee.

## Templates

Un nouveau partial, `src/templates/partials/documents/_entrepreneur_fields.html`, regroupe l'affichage des pieces entrepreneur. Les libelles proviennent des champs du formulaire et les pieces obligatoires sont signalees par un asterisque. Il rappelle egalement de regrouper les pieces de plusieurs signataires ou beneficiaires dans un seul fichier. Les garanties, le recu d'acompte et la fiche de demande n'y sont pas repetes : ils restent dans la section commune « Autres justificatifs » et sont facultatifs.

Les trois modales suivantes incluent ce partial si `is_entrepreneur` est vrai ; sinon, elles conservent le bloc « Emploi & Revenus » et les bulletins de paie :

- `src/templates/modals/leads/upload_doc.html` ;
- `src/templates/modals/leads/upload_offre_doc.html` ;
- `src/templates/modals/leads/update_doc.html`.

Les sections communes, notamment identite, residence, releves bancaires, specimen et geolocalisation, restent partagees entre les deux profils.

## Migrations

La migration `client_app/migrations/0011_documents_attestation_regularite_fiscale_and_more.py` ajoute les champs de documents entrepreneur et met a jour le libelle des releves bancaires. La migration `client_app/migrations/0012_remove_documents_facture_proforma.py` retire le champ facture proforma qui a ete abandonne.

## Verifications executees

- `manage.py check` : aucun probleme Django signale.
- Test cible en shell Django : les champs bulletins sont requis pour `Salarie` et le champ KYC ne l'est pas ; pour `entrepreneur`, le KYC est requis et les bulletins ne le sont pas.
- Chargement Django des templates des trois modales et du nouveau partial : reussi.
- `makemigrations --check --dry-run` signale une modification en attente independante dans `commercial_app` concernant `Offre.date_expiration`. Elle n'est pas liee a cette mise a jour.

## Points a confirmer

- La checklist precise que les statuts sont demandes pour les formes SA, SARL et SNC. En l'absence d'un champ de forme juridique dans le profil client, le formulaire et le controle de completude les exigent actuellement pour tous les entrepreneurs. Une condition plus precise necessitera de stocker la forme juridique de l'entreprise.
- Les identites de tous les signataires et beneficiaires sont chacune envoyees dans un seul fichier. Pour permettre un upload distinct par personne, il faudrait remplacer cette convention par un modele de pieces jointes multiples.

# Reinitialisation du mot de passe oublie

## Objectif

Permettre a un utilisateur qui ne peut plus se connecter de demander un lien temporaire par e-mail, puis de choisir un nouveau mot de passe. Le parcours utilise les vues natives de Django pour la generation et la validation du jeton, au lieu de stocker un jeton personnalise.

## Parcours utilisateur

Le lien « Mot de passe oublie ? » de la modale de connexion ouvre le formulaire de demande. L'utilisateur entre son adresse e-mail. Django envoie un courriel uniquement si un compte actif correspondant peut se connecter, mais affiche la meme confirmation dans tous les cas pour ne pas reveler si l'adresse est inscrite.

Le lien du courriel contient l'identifiant utilisateur encode et un jeton signe temporaire. Django verifie ce lien avant d'afficher les champs du nouveau mot de passe. Les validateurs de mot de passe deja configures s'appliquent, puis Django enregistre le nouveau hash et affiche la confirmation finale. Un lien invalide ou expire est refuse.

## Fichiers concernes

- `src/auth_app/urls.py` declare les quatre etapes : demande, confirmation neutre, validation du jeton et confirmation finale. Des commentaires expliquent chaque route et les parametres transmis aux vues Django.
- `src/templates/modals/auth/login_simple_modal.html` relie le lien d'oubli de mot de passe a la route de demande.
- `src/templates/auth_templates/password_reset_page.html` gere trois rendus : le formulaire (demande d'e-mail ou choix du nouveau mot de passe), l'avertissement de lien invalide/expire et la confirmation sans formulaire. Les vues `password_reset_done` et `password_reset_complete` utilisent cette derniere branche avec des titres et messages differents. Les commentaires Django expliquent les blocs du template sans etre inclus dans le HTML envoye au navigateur.
- `src/templates/auth_templates/password_reset_email.txt` et `src/templates/auth_templates/password_reset_subject.txt` definissent le contenu texte et le sujet du message de reinitialisation.
- `src/koz_flow/settings.py` indique a Django que Nginx transmet le protocole HTTPS, pour generer des liens de reinitialisation HTTPS en production.
- `src/auth_app/tests.py` verifie l'envoi du courriel, la reponse neutre pour une adresse inconnue, le lien du formulaire de connexion et le changement de mot de passe avec un jeton valide.

## Securite et configuration

L'envoi utilise le backend SMTP deja configure dans les parametres Django. Les variables de connexion e-mail de production doivent etre presentes pour que le message sorte effectivement. Le backend e-mail memoire est active uniquement dans les tests. Les vues Django natives limitent la validite des jetons et evitent de creer une table ou une migration supplementaire.

## Verifications executees

- `manage.py test auth_app.tests.PasswordResetTests` : quatre tests reussis avec la base locale.
- `manage.py check` execute par le lanceur de tests : aucun probleme Django signale.

# Correction Nginx du simulateur de financement

## Probleme corrige

La politique Content-Security-Policy configuree dans `nginx.conf` n'autorisait pas `cdn.jsdelivr.net`, alors que `src/templates/base.html` charge Alpine.js depuis ce domaine. En production, le navigateur bloquait le script ; les interactions Alpine de `src/templates/financement/simulation_financement.html` (calculs, choix du financement et champs dynamiques) ne pouvaient donc pas fonctionner.

## Correction

Le domaine `https://cdn.jsdelivr.net` a ete ajoute a la directive `script-src` de la CSP Nginx. Les erreurs de console ont ensuite confirme qu'Alpine.js avait aussi besoin de `'unsafe-eval'` pour evaluer ses expressions avec son build CDN standard ; cette source a donc ete autorisee. La directive `connect-src` autorise `https://cdn.plyr.io` pour eviter le blocage de la source map de Plyr dans les outils de developpement du navigateur.

L'autorisation de `'unsafe-eval'` assouplit la CSP et reduit sa protection contre l'execution de scripts injectes. A terme, privilegier une version CSP-compatible d'Alpine ou une configuration sans evaluation dynamique si toutes les expressions du site le permettent.

Apres deploiement, verifier la configuration dans le conteneur avec `docker compose exec nginx nginx -t`, puis la recharger avec `docker compose exec nginx nginx -s reload`.

## Verification

- `git diff --check` : aucune erreur de whitespace.
- `nginx -t` et le rechargement ont ete executes sur le serveur avec succes. Nginx a affiche des avertissements de deprecation pour la syntaxe `listen ... http2`, sans empecher le rechargement.
