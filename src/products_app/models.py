from django.db import models
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.utils.text import slugify

# ============================================================
# CATÉGORIE PRODUIT (améliorée)
# ============================================================
class CategorieProducts(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        verbose_name="Image de la catégorie"
    )
    icone = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Icône FontAwesome (ex: fa-oil-can)",
        verbose_name="Icône"
    )
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    est_active = models.BooleanField(default=True, verbose_name="Catégorie active")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = "Catégorie de produit"
        verbose_name_plural = "Catégories de produits"
    
    def __str__(self):
        return self.nom if self.nom else "Catégorie sans nom"


# ============================================================
# MARQUE PRODUIT (nouveau !)
# ============================================================
class MarqueProduit(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom de la marque")
    logo = models.ImageField(
        upload_to='marques_produits/',
        blank=True,
        null=True,
        verbose_name="Logo de la marque"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    site_web = models.URLField(blank=True, null=True, verbose_name="Site web")
    est_active = models.BooleanField(default=True, verbose_name="Marque active")
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['nom']
        verbose_name = "Marque de produit"
        verbose_name_plural = "Marques de produits"
    
    def __str__(self):
        return self.nom


# ============================================================
# UNITÉ DE MESURE (nouveau !)
# ============================================================
class UniteProduit(models.Model):
    nom = models.CharField(max_length=50, verbose_name="Nom de l'unité")
    abreviation = models.CharField(max_length=10, verbose_name="Abréviation")
    
    class Meta:
        verbose_name = "Unité de produit"
        verbose_name_plural = "Unités de produits"
    
    def __str__(self):
        return self.abreviation


# ============================================================
# PRODUIT (version premium)
# ============================================================
class Products(models.Model):
    
    # ===== INFOS GÉNÉRALES =====
    categorie = models.ForeignKey(
        CategorieProducts,
        on_delete=models.CASCADE,
        related_name="produits",
        verbose_name="Catégorie"
    )
    marque = models.ForeignKey(
        MarqueProduit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="produits",
        verbose_name="Marque"
    )
    nom = models.CharField(max_length=200, verbose_name="Nom du produit")
    description = models.TextField(blank=True, null=True, verbose_name="Description détaillée")
    description_courte = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Description courte (pour les cartes)"
    )
    
    # ===== PRIX & STOCK =====
    prix = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0.0,
        verbose_name="Prix (FCFA)"
    )
    prix_promo = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name="Prix promo (FCFA)"
    )
    date_debut_promo = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Début de la promotion"
    )
    date_fin_promo = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fin de la promotion"
    )
    stock = models.IntegerField(default=0, verbose_name="Stock disponible")
    stock_min = models.IntegerField(
        default=5,
        verbose_name="Stock minimum (alerte)"
    )
    unite = models.ForeignKey(
        UniteProduit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="produits",
        verbose_name="Unité de vente"
    )
    
    # ===== IMAGE =====
    image_principale = models.ImageField(
        upload_to='produits/',
        verbose_name="Image principale"
    )
    
    # ===== COMPATIBILITÉ =====
    compatible_avec = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Ex: Toyota, Nissan, Mercedes",
        verbose_name="Véhicules compatibles"
    )
    
    # ===== TAGS & VISIBILITÉ =====
    tags = models.CharField(
        max_length=52,
        blank=True,
        null=True,
        help_text="Mots-clés séparés par des virgules",
        verbose_name="Tags (SEO)"
    )
    est_vedette = models.BooleanField(default=False, verbose_name="Produit en vedette")
    est_disponible = models.BooleanField(default=True, verbose_name="Disponible à la vente")
    est_nouveau = models.BooleanField(default=False, verbose_name="Nouveau produit")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    favoris_de = models.ManyToManyField(
        'auth_app.kozUser',
        related_name='produits_favoris',
        blank=True,
        limit_choices_to={'role': 'client'},
    )
    # ===== DATES =====
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        null=True,
        help_text="Laissez vide pour génération automatique"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            base = f"{self.nom} {self.marque.nom if hasattr(self, 'marque') else ''}"
            self.slug = slugify(base)
            # Vérifier l'unicité
            original = self.slug
            counter = 1
            while Products.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom
    
    class Meta:
        ordering = ['ordre', '-date_ajout']
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
    
    def __str__(self):
        return self.nom if self.nom else "Produit sans nom"
    
    # ===== PROPRIÉTÉS =====
    @property
    def prix_actuel(self):
        """Retourne le prix promo si en promo, sinon le prix normal"""
        if self.est_en_promo():
            return self.prix_promo
        return self.prix
    
    @property
    def est_en_stock(self):
        """Vérifie si le produit est en stock"""
        return self.stock > 0
    
    
    @property
    def pourcentage_reduction(self):
        if not self.prix_promo or self.prix_promo >= self.prix:
            return 0
        return int(((self.prix - self.prix_promo) / self.prix) * 100)
        
    @property
    def stock_alerte(self):
        """Vérifie si le stock est en dessous du seuil d'alerte"""
        return self.stock <= self.stock_min
    
    def est_en_promo(self):
        """Vérifie si le produit est actuellement en promotion"""
        if not self.prix_promo:
            return False
        if self.date_debut_promo and self.date_debut_promo > timezone.now():
            return False
        if self.date_fin_promo and self.date_fin_promo < timezone.now():
            return False
        return True
    
    def get_etoiles(self):
        """Retourne la note moyenne (à implémenter avec un modèle Avis)"""
        return 0
    
    def get_absolute_url(self):
        return reverse('products_app:detail-produit-slug', kwargs={'slug': self.slug})
    
    


# ============================================================
# IMAGES PRODUIT
# ============================================================
class ProductsImage(models.Model):
    product = models.ForeignKey(
        Products,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Produit"
    )
    image = models.ImageField(
        upload_to="products_images/",
        verbose_name="Image"
    )
    alt_text = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Description courte de l'image pour l'accessibilité",
        verbose_name="Texte alternatif (SEO)"
    )
    ordre = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage",
        help_text="Plus le chiffre est petit, plus l'image est affichée en premier"
    )
    est_principale = models.BooleanField(
        default=False,
        verbose_name="Image principale",
        help_text="Cochez si cette image doit être l'image principale du produit"
    )
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    
    class Meta:
        ordering = ["ordre", "date_ajout"]
        verbose_name = "Image du produit"
        verbose_name_plural = "Images des produits"
    
    def __str__(self):
        return f"{self.product} - Image {self.ordre}"
    
    def save(self, *args, **kwargs):
        """Synchronise avec l'image principale du produit"""
        if self.est_principale:
            ProductsImage.objects.filter(product=self.product).exclude(pk=self.pk).update(est_principale=False)
            self.product.image_principale = self.image
            self.product.save(update_fields=['image_principale'])
        super().save(*args, **kwargs)


# ============================================================
# AVIS PRODUIT (pour plus tard)
# ============================================================
class ProductAvis(models.Model):
    product = models.ForeignKey(
        Products,
        on_delete=models.CASCADE,
        related_name="avis",
        verbose_name="Produit"
    )
    client = models.ForeignKey(
        'auth_app.kozUser',
        on_delete=models.CASCADE,
        related_name="avis_produits",
        verbose_name="Client"
    )
    note = models.PositiveSmallIntegerField(
        choices=[(i, f"{i} ⭐") for i in range(1, 6)],
        verbose_name="Note"
    )
    commentaire = models.TextField(verbose_name="Commentaire")
    est_approuve = models.BooleanField(default=False, verbose_name="Approuvé")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Avis produit"
        verbose_name_plural = "Avis produits"
    
    def __str__(self):
        return f"{self.client} - {self.product} ({self.note}⭐)"