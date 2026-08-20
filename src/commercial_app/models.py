from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse

class Offre(models.Model):
    client = models.ForeignKey("auth_app.kozUser", on_delete=models.CASCADE, related_name="offres")
    dossier = models.OneToOneField("client_app.documents", on_delete=models.CASCADE, related_name="offres", null=True, blank=True)
    demande_financement = models.OneToOneField("leads_app.demande_financement", on_delete=models.CASCADE, related_name="offre", null=True, blank=True)
    vehicule_propose = models.ForeignKey("vehicul_app.vehicul", related_name="offre", on_delete=models.CASCADE)
    
    montant_propose = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    prix_vehicule = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    apport_demande = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    montant_finance = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    duree_mois = models.IntegerField(default=0)
    mensualite = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    taux_interet = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    frais_dossier = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, default=0)
    frais_garantie = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, default=0)
    total_du = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, default=0)

    FINANCEMENT_TYPE_CHOISE = [
        ("maison", "Maison"),
        ("externe", "Externe")
    ]
    
    ENTREPRISE_FINANCE = [
                            ("fidelis", "Fidelis"),
                            ('alios', "Alios")
                                    ]
    
    financement_type = models.CharField(
        max_length=50, 
        choices=FINANCEMENT_TYPE_CHOISE, 
        null=True, 
        blank=True)
    
    # L'entrepise qui finance la demande
    financement_par = models.CharField(
        max_length=50, 
        choices=ENTREPRISE_FINANCE,
        null=True, blank=True
        )
    
    STATUTS_OFFRE = [
        ('brouillon', 'En cours de rédaction'),
        ('verification_document', "Dossier de l'offre en vérification"),
        ('en_attente_document', 'En attente de documents'),
        ('offre_document_rejete', 'Documents de l\'offre réjeté'),
        ('offre_document_valide', 'Documents de l\'offre validés'),
        ("offre_financement_fidelis", "offre financement chez Fidelis"),
        ("offre_financement_alios", "offre financement chez Alios"),
        ("offre_financement_maison", "offre financement KOZ Services"),
        ('envoyee', 'Envoyée'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
        ('expiree', 'Offre expirée'),
    ]
    TYPE_OFFRE_CHOICES = [
        ('simple', 'Offre simple'),
        ('demande', 'Offre liée à une demande'),
        ('offre_financement', 'Offre de financement'),
    ]
    statut = models.CharField(max_length=30, choices=STATUTS_OFFRE, default="brouillon")
    type_offre = models.CharField(max_length=20, choices=TYPE_OFFRE_CHOICES, default="simple")
    signature_client = models.ImageField(upload_to='signatures/', blank=True, null=True)
    
    date_expiration = models.DateTimeField(
        default=timezone.now() + timedelta(days=30)
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def get_absolute_url(self):
        return reverse('commercial_app:offre-detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        # ✅ Calcul automatique pour les offres de financement
        if self.type_offre == "offre_financement":
            self.total_du = (
                (self.mensualite or 0) * (self.duree_mois or 0)
                + (self.frais_dossier or 0)
                + (self.frais_garantie or 0)
            )
        
        # ✅ Vérification de l'expiration
        if self.date_expiration and self.date_expiration <= timezone.now():
            self.statut = 'expiree'
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Offre pour {self.client.nom_complet} - {self.statut}"