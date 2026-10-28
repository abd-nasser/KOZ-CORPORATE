# Django a déjà des classes pour gérer les utilisateurs, on va les personnaliser
from django.db import models
from django.urls import reverse
from auth_app.models import kozUser
from vehicul_app.models import Vehicul
from django.utils import timezone


class Maintenance(models.Model):
    
    # ----- TYPES DE MAINTENANCE -----
    TYPE_CHOICES = [
        ('vidange', 'Vidange'),
        ('revision', 'Révision complète'),
        ('pneumatiques', 'Pneumatiques'),
        ('freins', 'Freins/plaquettes'),
        ('climatisation', 'Climatisation'),
        ('batterie', 'Batterie'),
        ('autre', 'Autre'),
    ]
    
    # ----- STATUTS -----
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('planifiee', 'Planifiée'),
        ('confirmee', 'Confirmée'),
        ('en_cours', 'En cours'),
        ('effectuee', 'Effectuée'),
        ('depassee', 'Dépassée (non faite)'),
        ('annulee', 'Annulée'),
    ]
    
    # ----- PRIORITÉS (pour atelier) -----
    PRIORITE_CHOICES = [
        ('basse', 'Basse'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('urgente', 'Urgente'),
    ]
    
    # ----- ORIGINE VÉHICULE -----
    ORIGINE_CHOICES = [
        ('koz', 'Acheté chez KOZ'),
        ('externe', 'Véhicule extérieur'),
    ]
    
    # ----- CHAMPS -----
    client = models.ForeignKey(kozUser, on_delete=models.CASCADE, related_name='maintenances', limit_choices_to={'role': 'client'})
    
    # Infos véhicule
    vehicul = models.ForeignKey("vehicul_app.vehicul", on_delete=models.SET_NULL, related_name="maintenance", null=True, blank=True)
    service = models.ForeignKey("services_app.services", on_delete=models.SET_NULL,null=True,blank=True,related_name="maintenances")
    marque = models.CharField(max_length=50, null=True, blank=True)
    modele = models.CharField(max_length=100, blank=True, null=True)
    annee = models.IntegerField(null=True, blank=True)
    immatriculation = models.CharField(max_length=20, null=True, blank=True)
    kilometrage_actuel = models.IntegerField(null=True, blank=True)
    
    # Origine (remplace le boolean)
    origine = models.CharField(max_length=20, choices=ORIGINE_CHOICES, default='externe')
    
    # Détails maintenance
    type_maintenance = models.CharField(max_length=30, choices=TYPE_CHOICES)
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='normale')
    
    # Dates et kilométrage
    date_prevue = models.DateTimeField(null=True, blank=True)
    date_prochaine = models.DateTimeField(null=True, blank=True)
    date_derniere = models.DateField(null=True, blank=True)
    kilometrage_prochain = models.IntegerField(null=True, blank=True)
    kilometrage_dernier = models.IntegerField(null=True, blank=True)
    
    # Prix (si payant)
    montant_estime = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    montant_reel = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='planifiee')
    
    # Rappels
    rappel_envoye = models.BooleanField(default=False)
    date_rappel = models.DateField(null=True, blank=True)
    sms_envoye = models.BooleanField(default=False)
    email_envoye = models.BooleanField(default=False)
    
    # Notes
    notes_client = models.TextField(blank=True)
    notes_technicien = models.TextField(blank=True, verbose_name="Remarque technicien")
    
    # Champs techniques
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    effectue_par = models.ForeignKey(kozUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenances_effectuees', limit_choices_to={'role': 'commercial'})
    
    def __str__(self):
        return f"{self.client.nom_complet} - {self.marque} {self.modele} - {self.get_type_maintenance_display()}"
    
    @property
    def est_en_retard(self):
        # 1. Si aucune date n'est définie, la maintenance ne peut pas être en retard
        if not self.date_prochaine:
            return False
            
        # 2. Vérification du retard selon la date et le statut
        return self.date_prochaine < timezone.now() and self.statut not in ["effectuee", "annulee"]
        
    @property
    def km_restant(self):
        """Kilometre restant avant la prochaine maintenance"""
        return max(0, self.kilometrage_prochain - self.kilometrage_actuel)
    
    def get_absolute_url(self):
        return reverse('commercial_app:maintenance-detail', kwargs={'pk': self.pk})
    
    class Meta:
        ordering = ['date_prochaine']
        indexes = [
            models.Index(fields=['statut', 'date_prochaine']),
            models.Index(fields=['origine', 'statut']),
            models.Index(fields=['priorite', 'statut']),
        ]

from django.db import models
from django.urls import reverse

class Documents(models.Model):
    client = models.ForeignKey('auth_app.kozUser', on_delete=models.CASCADE, related_name='documents')
    demande_financement = models.OneToOneField('leads_app.demande_financement', on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    offre_financement = models.OneToOneField('commercial_app.offre', on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    
    # === IDENTITÉ & RÉSIDENCE ===
    cni_passeport = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Photocopie CNIB")
    justificatif_domicile = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Justificatif de résidence (eau, électricité, bail, certificat)")
    
    # === EMPLOI & REVENUS ===
    attestation_non_engagement = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Attestation de non-engagement")
    contrat_travail = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Contrat de travail")
    attestation_travail = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Attestation de travail (<3 mois)")
    
    # === BANQUE ===
    relevé_bancaire = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Relevé bancaire (24 mois) + RIB")
    specimen_signature = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Spécimen de recueil de signature")
    
    # === BULLETINS DE PAIE ===
    bulletin_1 = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Bulletin de paie (mois -3)", blank=True, null=True)
    bulletin_2 = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Bulletin de paie (mois -2)", blank=True, null=True)
    bulletin_3 = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Bulletin de paie (mois -1)", blank=True, null=True)
    
    # === GÉOLOCALISATION GPS (Remplace l'ancien FileField) ===
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Latitude GPS")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Longitude GPS")
    # Optionnel: On garde un fichier secours au cas où le client veut aussi importer un plan papier
    plan_geolocalisation = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Plan papier de géolocalisation (Optionnel)", blank=True, null=True)

    # === AUTRES JUSTIFICATIFS ===
    certificat_presence = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Certificat de présence au corps (FDS)", blank=True, null=True)
    garanties = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Garanties proposées (supports)", blank=True, null=True)
    recu_acompte = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Reçu des frais d'acompte de dossier", blank=True, null=True)
    fiche_demande = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Fiche de demande de financement", blank=True, null=True)

    # === PIÈCES COMPLÉMENTAIRES POUR LES ENTREPRENEURS ===
    formulaire_kyc = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Formulaire KYC", blank=True, null=True)
    consentement_bic = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Formulaire de consentement BIC", blank=True, null=True)
    extrait_rccm_ifu = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Extrait RCCM et IFU", blank=True, null=True)
    statuts_enregistres = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Statuts dûment enregistrés (SA, SARL, SNC)", blank=True, null=True)
    attestation_regularite_fiscale = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Attestation de régularité / situation fiscale", blank=True, null=True)
    pieces_identite_signataires = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Pièces d'identité de chaque signataire", help_text="Réunir les pièces des signataires dans un seul fichier.", blank=True, null=True)
    pieces_beneficiaires_effectifs = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Pièces des bénéficiaires effectifs (identité et/ou RCCM)", help_text="Réunir les justificatifs de chaque bénéficiaire effectif dans un seul fichier.", blank=True, null=True)
    cv_promoteur_gerant = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="CV du promoteur ou du gérant", blank=True, null=True)
    etats_financiers_1 = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="États financiers certifiés du dernier exercice", blank=True, null=True)
    etats_financiers_2 = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="États financiers certifiés de l'avant-dernier exercice", blank=True, null=True)
    etats_financiers_3 = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="États financiers certifiés du troisième exercice", blank=True, null=True)
    plan_affaires = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Plan d'affaires sur la durée du prêt", blank=True, null=True)
   
    STATUT_DOCS = [
        ("vide", "Dossier vide"),
        ('incomplet', 'Dossier incomplet'),
        ('complet', 'Dossier complet'),
        ('verification', 'En cours de vérification'),
        ('valide', 'Documents validés'),
        ('rejete', 'Documents rejetés'),
    ]
    statut_dossier = models.CharField(max_length=20, choices=STATUT_DOCS, default='vide')
    
    commentaire_rejet = models.TextField(
        blank=True, null=True,
        verbose_name="Commentaires du commercial ou de l'analyste",
        help_text="Utilisez ce champ pour indiquer les documents manquants, les erreurs à corriger, ou toute autre remarque pertinente pour le client."
    )        
    
    date_upload = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Dossier {self.client.nom_complet} - {self.statut_dossier}"
    
    def get_absolute_url(self):
        return reverse('leads_app:document-detail', kwargs={'pk': self.pk})

    @property
    def google_maps_url(self):
        """Raccourci pour le DG / Commercial afin d'ouvrir le lieu directement dans Google Maps"""
        if self.latitude and self.longitude:
            return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
        return None

    def verifier_completude(self):
        """Vérifie les documents requis et la présence d'une localisation."""
        has_coordinates = self.latitude is not None and self.longitude is not None
        has_location_document = bool(self.plan_geolocalisation)
        has_location = has_coordinates or has_location_document

        requis = [
            'cni_passeport',
            'justificatif_domicile',
            'relevé_bancaire',
            'specimen_signature',
        ]

        if self.client.profession_choisie == 'entrepreneur':
            requis.extend([
                'formulaire_kyc',
                'consentement_bic',
                'extrait_rccm_ifu',
                'statuts_enregistres',
                'attestation_regularite_fiscale',
                'pieces_identite_signataires',
                'pieces_beneficiaires_effectifs',
                'cv_promoteur_gerant',
                'etats_financiers_1',
                'etats_financiers_2',
                'etats_financiers_3',
                'plan_affaires',
            ])
        else:
            requis.extend([
                'attestation_non_engagement',
                'contrat_travail',
                'attestation_travail',
                'bulletin_1',
                'bulletin_2',
                'bulletin_3',
            ])
        
        if all(getattr(self, field_name) for field_name in requis) and has_location:
            self.statut_dossier = 'complet'
            self.save()
            return True
        return False