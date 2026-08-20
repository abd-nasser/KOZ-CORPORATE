from django.db import models

from django.db import models
from django.core.validators import FileExtensionValidator
from auth_app.models import kozUser


from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.core.validators import FileExtensionValidator

class Actualite(models.Model):
    """
    Modèle pour gérer les actualités de KOZ Services
    - Événements (réceptions, galas, lancements)
    - Nouvelles voitures
    - Communiqués
    """
    
    # ===== INFOS GÉNÉRALES =====
    titre = models.CharField(
        max_length=200,
        verbose_name="Titre de l'actualité"
    )
    sous_titre = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Sous-titre"
    )
    description = models.TextField(
        verbose_name="Description complète"
    )
    description_courte = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Description courte (pour les cartes)"
    )
    
    # ===== TYPES =====
    TYPE_CHOICES = [
        ('evenement', 'Événement'),
        ('nouveaute', 'Nouveauté / Lancement'),
        ('communique', 'Communiqué de presse'),
        ('offre', 'Offre spéciale'),
        ('reception', 'Réception / Gala'),
        ('promotion', 'Promotion'),
        ('autre', 'Autre'),
    ]
    
    type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default='nouveaute',
        verbose_name="Type d'actualité"
    )
    
    # ===== IMAGE PRINCIPALE =====
    image_principale = models.ImageField(
        upload_to='actualites/%Y/%m/%d/',
        verbose_name="Image principale"
    )
    
    # ===== IMAGES SUPPLÉMENTAIRES (max 5) =====
    image_1 = models.ImageField(
        upload_to='actualites/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="Image 2"
    )
    image_2 = models.ImageField(
        upload_to='actualites/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="Image 3"
    )
    image_3 = models.ImageField(
        upload_to='actualites/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="Image 4"
    )
    image_4 = models.ImageField(
        upload_to='actualites/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="Image 5"
    )
    image_5 = models.ImageField(
        upload_to='actualites/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="Image 6"
    )
    
    # ===== VIDÉO =====
    video_file = models.FileField(
        upload_to='actualites/videos/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['mp4', 'webm', 'mov', 'avi'])],
        verbose_name="Fichier vidéo",
        help_text="Formats : MP4, WebM, MOV"
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Lien YouTube/Vimeo",
        help_text="https://www.youtube.com/watch?v=..."
    )
    
    # ===== LIENS =====
    lien_externe = models.URLField(
        blank=True,
        null=True,
        verbose_name="Lien externe",
        help_text="Rediriger vers une page externe"
    )
    
    lien_interne = models.URLField(
            blank=True,
            null=True,
            verbose_name="Lien interne",
            help_text="Rediriger vers une page interne"
        )
    
    # ===== DATES =====
    date_evenement = models.DateTimeField(
        verbose_name="Date de l'événement",
        help_text="Date à laquelle l'événement a lieu"
    )
    date_publication = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date de publication"
    )
    date_fin = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Date de fin",
        help_text="Pour les offres ou événements avec durée"
    )
    
    # ===== VISIBILITÉ =====
    est_publie = models.BooleanField(
        default=True,
        verbose_name="Publié"
    )
    est_vedette = models.BooleanField(
        default=False,
        verbose_name="Mettre en vedette"
    )
    ordre = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )
    
    # ===== STATISTIQUES =====
    vues = models.PositiveIntegerField(
        default=0,
        verbose_name="Nombre de vues"
    )
    
    # ===== MÉTADONNÉES =====
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_evenement', '-date_publication']
        verbose_name = "Actualité"
        verbose_name_plural = "Actualités"
    
    def __str__(self):
        return self.titre
    
    @property
    def images_list(self):
        """Retourne la liste des images disponibles (max 5)"""
        images = []
        if self.image_principale:
            images.append(self.image_principale)
        for i in range(1, 6):
            image = getattr(self, f'image_{i}', None)
            if image:
                images.append(image)
        return images
    
    @property
    def nb_images(self):
        """Nombre d'images disponibles"""
        return len(self.images_list)
    
    @property
    def est_en_cours(self):
        """Vérifie si l'événement est en cours"""
        if not self.date_fin:
            return self.date_evenement <= timezone.now()
        return self.date_evenement <= timezone.now() <= self.date_fin
    
    @property
    def est_a_venir(self):
        """Vérifie si l'événement est à venir"""
        return self.date_evenement > timezone.now()
    
    @property
    def type_icone(self):
        """Retourne l'icône selon le type"""
        icones = {
            'evenement': 'fa-calendar-day',
            'nouveaute': 'fa-sparkles',
            'communique': 'fa-bullhorn',
            'offre': 'fa-tag',
            'reception': 'fa-glass-cheers',
            'promotion': 'fa-percent',
            'autre': 'fa-info-circle',
        }
        return icones.get(self.type, 'fa-info-circle')
    
    @property
    def type_couleur(self):
        """Retourne la couleur selon le type"""
        couleurs = {
            'evenement': 'blue',
            'nouveaute': 'emerald',
            'communique': 'purple',
            'offre': 'amber',
            'reception': 'pink',
            'promotion': 'red',
            'autre': 'gray',
        }
        return couleurs.get(self.type, 'gray')
    
    @property
    def type_couleur_hex(self):
        """Retourne la couleur hex selon le type"""
        couleurs = {
            'blue': '#3b82f6',
            'emerald': '#10b981',
            'purple': '#8b5cf6',
            'amber': '#f59e0b',
            'pink': '#ec4899',
            'red': '#ef4444',
            'gray': '#6b7280',
        }
        return couleurs.get(self.type_couleur, '#6b7280')

class Temoignage(models.Model):
    
    SOURCE_CHOICES = [
            ('site', 'Site KOZ'),
            ('facebook', 'Facebook'),
            ('google', 'Google Maps'),
            ('whatsapp', 'WhatsApp'),
            ('instagram', 'Instagram'),
        ]
    """Témoignage client"""
    client = models.ForeignKey(
        kozUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='temoignages'
    )
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    photo = models.ImageField(
        upload_to='temoignages/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="Photo"
    )
    message = models.TextField(verbose_name="Témoignage")
    note = models.PositiveSmallIntegerField(
        choices=[(i, f"{i} ⭐") for i in range(1, 6)],
        default=5,
        verbose_name="Note"
    )
    source = models.CharField(
        max_length=50,
        choices=SOURCE_CHOICES,
        default='site',
        verbose_name="Source"
    )
    est_approuve = models.BooleanField(default=False, verbose_name="Approuvé")
    est_vedette = models.BooleanField(default=False, verbose_name="Mettre en vedette")
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Témoignage"
        verbose_name_plural = "Témoignages"
    
    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.note}⭐"


class AvisReseau(models.Model):
    """Avis provenant des réseaux sociaux"""
    RESEAUX_CHOICES = [
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('google', 'Google Maps'),
        ('whatsapp', 'WhatsApp'),
        ('tiktok', 'TikTok'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
    ]
    
    reseau = models.CharField(max_length=20, choices=RESEAUX_CHOICES, verbose_name="Réseau social")
    nom_utilisateur = models.CharField(max_length=100, verbose_name="Nom d'utilisateur")
    message = models.TextField(verbose_name="Message")
    date_publication = models.DateTimeField(verbose_name="Date de publication")
    image = models.ImageField(
        upload_to='avis_reseaux/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="Image/screenshot"
    )
    lien = models.URLField(blank=True, null=True, verbose_name="Lien vers le post")
    est_actif = models.BooleanField(default=True, verbose_name="Afficher")
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_publication']
        verbose_name = "Avis réseau social"
        verbose_name_plural = "Avis réseaux sociaux"
    
    def __str__(self):
        return f"{self.get_reseau_display()} - {self.nom_utilisateur}"


class VideoTemoignage(models.Model):
    """Vidéo de témoignage ou présentation"""
    titre = models.CharField(max_length=200, verbose_name="Titre de la vidéo")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    # Option 1 : Vidéo uploadée
    video_file = models.FileField(
        upload_to='videos/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['mp4', 'webm', 'mov', 'avi'])],
        verbose_name="Fichier vidéo",
        help_text="MP4, WebM, MOV (max 100MB)"
    )
    
    # Option 2 : Lien externe (YouTube, Vimeo)
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Lien YouTube/Vimeo",
        help_text="https://www.youtube.com/watch?v=..."
    )
    
    # Option 3 : Intégration embed (iframe)
    embed_code = models.TextField(
        blank=True,
        null=True,
        verbose_name="Code d'intégration",
        help_text="Code iframe YouTube ou autre"
    )
 
    duree = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Durée en secondes",
        verbose_name="Durée"
    )
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['ordre', 'date_ajout']
        verbose_name = "Vidéo"
        verbose_name_plural = "Vidéos"
    
    def __str__(self):
        return self.titre
    
    @property
    def duree_formatee(self):
        if not self.duree:
            return "00:00"
        minutes = self.duree // 60
        secondes = self.duree % 60
        return f"{minutes:02d}:{secondes:02d}"
    
    @property
    def video_mime_type(self):
        """Retourne le type MIME de la vidéo"""
        if not self.video_file:
            return None
        import os
        ext = os.path.splitext(self.video_file.name)[1].lower()
        mime_types = {
            '.mp4': 'video/mp4',
            '.webm': 'video/webm',
            '.mov': 'video/quicktime',
            '.avi': 'video/x-msvideo',
        }
        return mime_types.get(ext, 'video/mp4')
    
    
# home_app/models.py

# home_app/models.py

class RendezVous(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirme', 'Confirmé'),
        ('annule', 'Annulé'),
        ('termine', 'Terminé'),
    ]
    
    client = models.ForeignKey(
        'auth_app.kozUser',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='rendez_vous',
        verbose_name="Client"
    )
    nom = models.CharField(max_length=255, verbose_name="Nom", null=True, blank=True )
    prenom = models.CharField(max_length=255, verbose_name="Prenom", null=True, blank=True)
    telephone = models.CharField(max_length=255, verbose_name="telephone", null=True, blank=True)
    date_rendez_vous = models.DateTimeField(verbose_name="Date et heure")
    duree = models.PositiveIntegerField(default=60, verbose_name="Durée (minutes)")
    motif = models.CharField(max_length=255, verbose_name="Motif")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date_rendez_vous']
        verbose_name = "Rendez-vous"
        verbose_name_plural = "Rendez-vous"
    
    def __str__(self):
        return f"{self.client} - {self.date_rendez_vous.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def est_passe(self):
        from django.utils import timezone
        return self.date_rendez_vous < timezone.now()
    
    @property
    def est_a_venir(self):
        from django.utils import timezone
        return self.date_rendez_vous >= timezone.now()