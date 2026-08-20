# Django a déjà des classes pour gérer les utilisateurs, on va les personnaliser
from django.db import models
from django.urls import reverse
from auth_app.models import kozUser
from vehicul_app.models import Vehicul
from datetime import timezone, timedelta, datetime


class Maintenance(models.Model):
    
    # ----- TYPES DE MAINTENANCE -----
    TYPE_CHOICES = [
        ('vidange', 'Vidange'),
        ('revision', 'Révision complète'),
        ('pneumatiques', 'Pneumatiques'),
        ('freins', 'Freins/plaquettes'),
        ('climatisation', 'Climatisation'),
        ('batterie', 'Batterie'),
        ('courroie', 'Courroie de distribution'),
        ('autre', 'Autre'),
    ]
    
    # ----- STATUTS -----
    STATUT_CHOICES = [
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
    marque = models.CharField(max_length=50)
    modele = models.CharField(max_length=100)
    annee = models.IntegerField()
    immatriculation = models.CharField(max_length=20, null=True, blank=True)
    kilometrage_actuel = models.IntegerField()
    
    # Origine (remplace le boolean)
    origine = models.CharField(max_length=20, choices=ORIGINE_CHOICES, default='externe')
    
    # Détails maintenance
    type_maintenance = models.CharField(max_length=30, choices=TYPE_CHOICES)
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='normale')
    
    # Dates et kilométrage
    date_prevue = models.DateField(null=True, blank=True)
    date_prochaine = models.DateField()
    date_derniere = models.DateField(null=True, blank=True)
    kilometrage_prochain = models.IntegerField()
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
        """True si la date de la maintenance est dépassée"""
        return self.date_prochaine < datetime.now().date() and self.statut not in ["effectuee", "annulee"]
    
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
    quittance_salaire = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="quittance de salaire")
    
    # === BANQUE ===
    relevé_bancaire = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Relevé bancaire (12 mois) + RIB")
    specimen_signature = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Spécimen de recueil de signature")
    
      # ===== EMPLOI & REVENUS =====
    bulletin_1 = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Bulletin de paie (mois -3)", blank=True, null=True)
    bulletin_2 = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Bulletin de paie (mois -2)", blank=True, null=True)
    bulletin_3 = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Bulletin de paie (mois -1)", blank=True, null=True)
    
    
    # === AUTRES JUSTIFICATIFS ===
    certificat_presence = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Certificat de présence au corps (âge départ retraite)", blank=True, null=True)
    geolocalisation = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Plan de géolocalisation", blank=True, null=True)
    garanties = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Garanties proposées (supports)", blank=True, null=True)
    recu_acompte = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Reçu des frais d'acompte de dossier", blank=True, null=True)
    fiche_demande = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Fiche de demande de financement", blank=True, null=True)
    
    # Statut (inchangé)
    STATUT_DOCS = [
        ("vide", "Dossier vide"),
        ('incomplet', 'Dossier incomplet'),
        ('complet', 'Dossier complet'),
        ('verification', 'En cours de vérification'),
        ('valide', 'Documents validés'),
        ('rejete', 'Documents rejetés'),
    ]
    statut_dossier = models.CharField(max_length=20, choices=STATUT_DOCS, default='vide')
    
    commentaire_rejet = models.TextField(blank=True, null=True,
                                    verbose_name="Commentaires du commercial ou de l'analyste",
                                    help_text="Utilisez ce champ pour indiquer les documents manquants, les erreurs à corriger, ou toute autre remarque pertinente pour le client.")        
                                    
    
    date_upload = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Dossier {self.client.nom_complet} - {self.statut_dossier}"
    
    def get_absolute_url(self):
        return reverse('leads_app:document-detail', kwargs={'pk': self.pk})
    
    def verifier_completude(self):
        """Vérifie si les documents OBLIGATOIRES sont présents"""
        requis = [
            self.cni_passeport,
            self.justificatif_domicile,
            self.attestation_non_engagement,
            self.contrat_travail,
            self.attestation_travail,
            self.quittance_salaire,
            self.relevé_bancaire,
            self.specimen_signature,
            self.bulletin_1,
            self.bulletin_2,
            self.bulletin_3
        ]
        if all(requis):
            self.statut_dossier = 'complet'
            self.save()
            return True
        return False