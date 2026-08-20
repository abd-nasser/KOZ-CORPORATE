from django import forms
from .models import TypesServices, Services, ServiceImages, ServiceAvis


# ============================================================
# FORMULAIRES EXISTANTS (TypesServices, Services)
# ============================================================
class TypesServicesForm(forms.ModelForm):
    class Meta:
        model = TypesServices
        fields = ['nom', 'description', 'icone', 'couleur', 'est_actif']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'description': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 3}),
            'icone': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'fa-tools'}),
            'couleur': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'type': 'color'}),
            'est_actif': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
        }


class ServicesForm(forms.ModelForm):
    class Meta:
        model = Services
        fields = [
            'types', 'nom', 'description', 'description_courte',
            'prix', 'prix_promo', 'unite', 'duree_estimee', 'periodicite',
            'est_disponible', 'est_vedette', 'ordre', 'image_principale',
            'compatible_vehicules', 'est_forfait', 'services_inclus'
        ]
        widgets = {
            'types': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'nom': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'description': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 4}),
            'description_courte': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'prix': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            'prix_promo': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            'unite': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'duree_estimee': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            'periodicite': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'est_disponible': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
            'est_vedette': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
            'ordre': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            'image_principale': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'compatible_vehicules': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Toyota, Nissan, Mercedes'}),
            'est_forfait': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
            'services_inclus': forms.SelectMultiple(attrs={'class': 'select select-bordered w-full'}),
        }
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False
    


# ============================================================
# ✅ NOUVEAU : FORMULAIRE POUR LES IMAGES DE SERVICE
# ============================================================
class ServiceImagesForm(forms.ModelForm):
    """Formulaire pour ajouter/modifier une image de service"""
    
    class Meta:
        model = ServiceImages
        fields = ['image', 'alt_text', 'ordre', 'est_principale']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'file-input file-input-bordered w-full',
                'accept': 'image/*'
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Description de l\'image pour le SEO'
            }),
            'ordre': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'min': 0,
                'placeholder': '0'
            }),
            'est_principale': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre le champ image obligatoire à la création
        if not self.instance.pk:
            self.fields['image'].required = True


# ============================================================
# ✅ NOUVEAU : FORMULAIRE POUR LES AVIS DE SERVICE
# ============================================================
class ServiceAvisForm(forms.ModelForm):
    """Formulaire pour laisser un avis sur un service"""
    
    class Meta:
        model = ServiceAvis
        fields = ['note', 'commentaire']
        widgets = {
            'note': forms.Select(attrs={
                'class': 'select select-warning w-full'
            }),
            'commentaire': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 4,
                'placeholder': 'Partagez votre expérience avec ce service...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['note'].choices = [(i, f"{i} ⭐") for i in range(1, 6)]
        self.fields['commentaire'].required = True


# ============================================================
# ✅ FORMULAIRE POUR L'APPROBATION DES AVIS (pour le DG)
# ============================================================
class ServiceAvisApprobationForm(forms.ModelForm):
    """Formulaire pour approuver/rejeter un avis client"""
    
    class Meta:
        model = ServiceAvis
        fields = ['est_approuve']
        widgets = {
            'est_approuve': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['est_approuve'].label = "Approuver cet avis"
        