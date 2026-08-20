from django.db import models
from django.utils import timezone
from datetime import timedelta

class TypesServices(models.Model):
    """
    Types de services proposés par KOZ
    Ex: Maintenance, Financement, Pièces détachées, Carrosserie, etc.
    """
    nom = models.CharField(max_length=150, verbose_name="Nom du type")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    icone = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Classe FontAwesome (ex: fa-tools)",
        verbose_name="Icône"
    )
    couleur = models.CharField(
        max_length=7,
        default='#3b82f6',
        help_text="Couleur en hexadécimal (ex: #3b82f6)",
        verbose_name="Couleur"
    )
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    
    class Meta:
        verbose_name = "Type de service"
        verbose_name_plural = "Types de services"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class Services(models.Model):
    """
    Services proposés par KOZ (offres de services)
    """
    
    # Types de services
    types = models.ForeignKey(
        TypesServices, 
        on_delete=models.CASCADE, 
        related_name='services',
        blank=True,
        null=True,
        verbose_name="Type de service"
    )
    
    # Informations générales
    nom = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nom du service")
    description = models.TextField(blank=True, null=True, verbose_name="Description du service")
    description_courte = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Description courte (pour les cartes)"
    )
    
    # Prix
    prix = models.DecimalField(
        max_digits=12, 
        decimal_places=0, 
        default=0,
        blank=True,
        null=True,
        verbose_name="Prix (FCFA)",
    )
    prix_promo = models.DecimalField(
        max_digits=12, 
        decimal_places=0, 
        null=True, 
        blank=True,
        verbose_name="Prix promo (FCFA)"
    )
    unite = models.CharField(
        max_length=50,
        default="service",
        blank=True,
        null=True,
        help_text="Ex: service, heure, mois, pièce",
        verbose_name="Unité"
    )
    
    # Durée et périodicité
    duree_estimee = models.PositiveIntegerField(
        default=30,
        blank=True,
        null=True,
        help_text="Durée estimée en minutes",
        verbose_name="Durée estimée"
    )
    periodicite = models.CharField(
        max_length=50,
        choices=[
            ('unique', 'Unique'),
            ('mensuel', 'Mensuel'),
            ('trimestriel', 'Trimestriel'),
            ('semestriel', 'Semestriel'),
            ('annuel', 'Annuel'),
        ],
        default='unique',
        blank=True,
        null=True,
        verbose_name="Périodicité"
    )
    
    # Disponibilité
    est_disponible = models.BooleanField(default=True, blank=True, null=True, verbose_name="Service disponible")
    est_vedette = models.BooleanField(default=False, blank=True, null=True, verbose_name="Service en vedette")
    ordre = models.PositiveIntegerField(default=0, blank=True, null=True, verbose_name="Ordre d'affichage")
    
    # Images
    image_principale = models.ImageField(
        upload_to='services/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="Image principale"
    )
    
    # Compatibilité
    compatible_vehicules = models.TextField(
        blank=True,
        null=True,
        help_text="Marques ou modèles compatibles (séparés par des virgules)",
        verbose_name="Véhicules compatibles"
    )
    
    # Forfait
    est_forfait = models.BooleanField(default=False, blank=True, null=True, verbose_name="Est un forfait")
    services_inclus = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='inclus_dans',
        verbose_name="Services inclus (pour les forfaits)"
    )
    
    # Dates
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    
    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        return f"{self.nom} ({self.get_periodicite_display()})"
    
    @property
    def prix_affiche(self):
        """Retourne le prix promo si disponible, sinon le prix normal"""
        return self.prix_promo if self.prix_promo else self.prix
    
    @property
    def est_en_promo(self):
        """Vérifie si le service est en promotion"""
        return self.prix_promo is not None and self.prix_promo < self.prix


class ServiceImages(models.Model):
    """
    Images supplémentaires pour un service
    """
    service = models.ForeignKey(
        Services, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name="Service"
    )
    image = models.ImageField(
        upload_to='services_images/%Y/%m/%d/',
        verbose_name="Image"
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Texte alternatif (SEO)"
    )
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    est_principale = models.BooleanField(default=False, verbose_name="Image principale")
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    
    class Meta:
        ordering = ['ordre', 'date_ajout']
        verbose_name = "Image du service"
        verbose_name_plural = "Images des services"
    
    def __str__(self):
        return f"Image {self.ordre} - {self.service.nom}"
    
    def save(self, *args, **kwargs):
        """Si cette image est marquée comme principale, désactiver les autres"""
        if self.est_principale:
            ServiceImages.objects.filter(service=self.service).exclude(pk=self.pk).update(est_principale=False)
        super().save(*args, **kwargs)


class ServiceAvis(models.Model):
    """
    Avis clients sur les services
    """
    service = models.ForeignKey(
        Services, 
        on_delete=models.CASCADE, 
        related_name='avis',
        verbose_name="Service"
    )
    client = models.ForeignKey(
        'auth_app.kozUser',
        on_delete=models.CASCADE,
        related_name='avis_services',
        verbose_name="Client"
    )
    note = models.PositiveSmallIntegerField(
        choices=[(i, f"{i} étoile{'s' if i > 1 else ''}") for i in range(1, 6)],
        verbose_name="Note"
    )
    commentaire = models.TextField(verbose_name="Commentaire")
    est_approuve = models.BooleanField(default=False, verbose_name="Approuvé")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Avis sur service"
        verbose_name_plural = "Avis sur les services"
    
    def __str__(self):
        return f"{self.client.nom_complet} - {self.service.nom} ({self.note}★)"