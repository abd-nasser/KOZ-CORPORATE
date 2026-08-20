from django.db import models
from django.urls import reverse
from django.utils.text import slugify
class Marque(models.Model):
    nom = models.CharField(max_length=100, null=True, blank=True)
    logo = models.ImageField(upload_to="marques/", null=True, blank=True)
    
    def __str__(self):
        return self.nom if self.nom else "Marque sans nom"

class TypeVehicule(models.Model):
    """
    Types de véhicules : SUV, Berline, Coupé, Break, Pick-up, etc.
    """
    nom = models.CharField(
        max_length=50,
        verbose_name="Nom du type",
        help_text="Ex: SUV, Berline, Coupé"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description"
    )
    
    image = models.ImageField(
            upload_to='type_vehicule_images/%Y/%m/%d/',
            verbose_name="image",
            blank=True,
            null=True,
        )
    
    icone = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Icône FontAwesome (ex: fa-car, fa-truck)",
        verbose_name="Icône"
    )
    ordre = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = "Type de véhicule"
        verbose_name_plural = "Types de véhicules"
    
    def __str__(self):
        return self.nom
    
    
class Vehicul(models.Model):
    
    TYPES_CARBURANT_CHOICES = [
        ('essence', "Essence"),
        ("diesel", "Diesel"),
        ("electrique", 'Electrique')
    ]
    
    type_vehicule = models.ForeignKey(  # ← ✅ NOUVEAU CHAMP
        TypeVehicule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehicules',
        verbose_name="Type de véhicule"
    )
    
    marque = models.ForeignKey(Marque, on_delete=models.CASCADE, related_name='vehicul')
    modele = models.CharField(max_length=100)
    annee = models.IntegerField()
    stock = models.IntegerField(null=True, blank=True)
    stock_min = models.IntegerField(
            default=1,
            verbose_name="Stock minimum (alerte)"
        )
    prix = models.DecimalField(max_digits=12, decimal_places=0)
    kilometrage = models.IntegerField()
    carburant = models.CharField(max_length=20, choices=TYPES_CARBURANT_CHOICES, default="essence")
    
    # ========== IMAGE PRINCIPALE (conservée) ==========
    image_principale = models.ImageField(upload_to='vehicules/')
    
    
    disponible = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    actualite = models.BooleanField(default=False)
    est_vedette = models.BooleanField(default=False)
    favoris_de = models.ManyToManyField(
    'auth_app.kozUser',
    related_name='vehicules_favoris',
    blank=True,
    limit_choices_to={'role': 'client'},
)
    
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        null=True,
        help_text="Laissez vide pour génération automatique"
    )
    
    # ✅ Propriété qui choisit la bonne image
    @property
    def display_image(self):
        principale = self.images.filter(est_principale=True).first()
        if principale:
            return principale.image
        return self.image_principale
    
    @property
    def est_en_stock(self):
        """Vérifie si le produit est en stock"""
        return self.stock > 0
    
    @property
    def stock_alerte(self):
        """Vérifie si le stock est en dessous du seuil d'alerte"""
        return self.stock <= self.stock_min
        
    def __str__(self):
        marque_nom = self.marque.nom if self.marque else "?"
        modele_nom = self.modele if self.modele else "?"
        return f"{marque_nom} {modele_nom}"
    
    def get_absolute_url(self):
        return reverse('vehicul_app:site-vehicul-detail-slug', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            base = f"{self.marque.nom} {self.modele} {self.annee}"
            self.slug = slugify(base)
            # Gérer l'unicité
            original = self.slug
            counter = 1
            while Vehicul.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
        
        

# ============================================================
# ✅ NOUVEAU MODÈLE : IMAGES MULTIPLES POUR VÉHICULE
# ============================================================
class VehiculeImage(models.Model):
    """
    Modèle pour gérer plusieurs images par véhicule.
    Permet une galerie illimitée avec pagination.
    """
    vehicule = models.ForeignKey(
        Vehicul, 
        on_delete=models.CASCADE, 
        related_name='images'  # → vehicule.images.all()
    )
    
    image = models.ImageField(
        upload_to='vehicules_images/%Y/%m/%d/',
        verbose_name="image"
    )
    
    alt_text = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name="Texte alternatif (SEO)",
        help_text="Description courte de l'image pour l'accessibilité"
    )
    
    ordre = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage",
        help_text="Plus le chiffre est petit, plus l'image est affichée en premier"
    )
    
    est_principale = models.BooleanField(
        default=False,
        verbose_name="Image principale",
        help_text="Cochez si cette image doit être l'image principale du véhicule",
    
    )
    
    date_ajout = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'ajout"
    )
    
    class Meta:
        ordering = ['ordre', 'date_ajout']
        verbose_name = "Image du véhicule"
        verbose_name_plural = "Images des véhicules"
    
    def __str__(self):
        return f"{self.vehicule} - Image {self.ordre}"
    
    
     
    
 
