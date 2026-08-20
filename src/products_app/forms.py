from django import forms
from .models import CategorieProducts, MarqueProduit, UniteProduit, Products, ProductsImage


class CategorieProductsForm(forms.ModelForm):
    class Meta:
        model = CategorieProducts
        fields = ['nom', 'description', 'image', 'icone', 'ordre', 'est_active']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Nom de la catégorie'}),
            'description': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 3, 'placeholder': 'Description de la catégorie'}),
            'image': forms.ClearableFileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'icone': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'fa-oil-can'}),
            'ordre': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'min': 0}),
            'est_active': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
        }


class MarqueProduitForm(forms.ModelForm):
    class Meta:
        model = MarqueProduit
        fields = ['nom', 'logo', 'description', 'site_web', 'est_active']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Nom de la marque'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'description': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 3, 'placeholder': 'Description de la marque'}),
            'site_web': forms.URLInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'https://example.com'}),
            'est_active': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
        }


class UniteProduitForm(forms.ModelForm):
    class Meta:
        model = UniteProduit
        fields = ['nom', 'abreviation']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Nom de l’unité'}),
            'abreviation': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Ex: L, kg, pcs'}),
        }


class ProductsForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = [
            'categorie', 'marque', 'nom', 'description', 'description_courte',
            'prix', 'prix_promo', 'date_debut_promo', 'date_fin_promo',
            'stock', 'stock_min', 'unite', 'image_principale',
            'compatible_avec', 'tags', 'est_vedette', 'est_disponible',
            'est_nouveau', 'ordre'
        ]
        widgets = {
            'categorie': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'marque': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'nom': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Nom du produit'}),
            'description': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 4, 'placeholder': 'Description détaillée du produit'}),
            'description_courte': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Description courte'}),
            'prix': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Prix du produit'}),
            'prix_promo': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Prix promo'}),
            'date_debut_promo': forms.DateTimeInput(attrs={'class': 'input input-bordered w-full', 'type': 'datetime-local'}),
            'date_fin_promo': forms.DateTimeInput(attrs={'class': 'input input-bordered w-full', 'type': 'datetime-local'}),
            'stock': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Stock disponible'}),
            'stock_min': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Stock minimum'}),
            'unite': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'image_principale': forms.ClearableFileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'compatible_avec': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Ex: Toyota, Nissan, Mercedes'}),
            'tags': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Mots-clés séparés par des virgules'}),
            'est_vedette': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
            'est_disponible': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
            'est_nouveau': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
            'ordre': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'min': 0}),
        }


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductsImage
        fields = ['image', 'alt_text', 'ordre', 'est_principale']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'alt_text': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Description de l\'image (SEO)'}),
            'ordre': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'min': 0}),
            'est_principale': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
        }
