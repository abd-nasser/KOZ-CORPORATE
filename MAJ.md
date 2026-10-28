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
