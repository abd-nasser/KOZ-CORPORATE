from django import forms
from django.forms import inlineformset_factory
from .models import Vehicul, Marque, VehiculeImage


class MarqueForm(forms.ModelForm):
    class Meta:
        model = Marque
        fields = ["nom","logo"]
        widgets = {
            "nom": forms.TextInput(attrs={"class":"input input-bordered w-full", "placeholder":"Saisir le nom de la marque"}),
            "logo": forms.ClearableFileInput(attrs={"class":"file-input file-input-bordered w -full"}),
        }
        
    def clean_nom(self):
        """Vérifie que le champ nom n'est pas vide"""
        nom = self.cleaned_data.get('nom')
        if not nom or not nom.strip():
            raise forms.ValidationError("Le nom de la marque est obligatoire")
        return nom.strip()
    
    
from .models import TypeVehicule

class TypeVehiculeForm(forms.ModelForm):
    class Meta:
        model = TypeVehicule
        fields = ['nom', 'description', 'icone', 'image', 'ordre']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'description': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 3}),
            'icone': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'fa-car'}),
            'ordre': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'min': 0}),
            'image':forms.ClearableFileInput(attrs={"class":"file-input file-input-bordered w-full"}),
        }
class VehiculForm(forms.ModelForm):
    class Meta:
        model = Vehicul
        fields = ["marque","modele","type_vehicule","annee", "stock",
                  "prix", "kilometrage", "carburant","actualite","est_vedette",
                  "image_principale",
                  "disponible", "description",
                  ]
        
        widgets = {
            "marque":forms.Select(attrs={"class":"select select-bordered w-full"}),
            "ype_vehicule":forms.Select(attrs={"class":"select select-bordered w-full"}),
            "modele": forms.TextInput(attrs={"class":"input input-bordered w-full", "placeholder":"Saisir le modèle"}),
            "annee": forms.NumberInput(attrs={"class":"input input-bordered w-full", "placeholder":"Saisir l'année"}),
            "stock":forms.NumberInput(attrs={"class":"input input-bordered w-full", "placeholder":"nombre"}),
            "prix": forms.NumberInput(attrs={"class":"input input-bordered w-full", "placeholder":"Saisir le prix"}),
            "kilometrage": forms.NumberInput(attrs={"class":"input input-bordered w-full", "placeholder":"Saisir le kilométrage"}),
            "carburant": forms.Select(attrs={"class":"select select-bordered w-full"}),
            "image_principale": forms.ClearableFileInput(attrs={"class":"file-input file-input-bordered w-full"}),
            "actualite":forms.CheckboxInput(attrs={"class":"checkbox checkbox-primary"}),
            "disponible": forms.CheckboxInput(attrs={"class":"checkbox checkbox-primary"}),
            "est_vedette":forms.CheckboxInput(attrs={"class":"checkbox checkbox-primary"}),
            "description": forms.Textarea(attrs={"class":"textarea textarea-info w-full", "placeholder":"Saisir la description", "rows": 4}),
            }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
          # Configuration des classes CSS pour chaque type de champ
        config = {
            forms.TextInput: 'input input-bordered w-full',
            forms.Select: 'select select-bordered w-full',
            forms.CheckboxInput: 'checkbox checkbox-primary',
            forms.ClearableFileInput: 'file-input file-input-bordered w-full',
            forms.NumberInput: 'input input-bordered w-full',
            forms.Textarea: 'textarea textarea-info w-full',
        }
        
        for field_name, field in self.fields.items():
            # Récupère la classe selon le type du widget
            widget_type = type(field.widget)
            css_class = config.get(widget_type, 'input input-bordered w-full')
            field.widget.attrs['class'] = css_class
            
            # Ajoute un placeholder pour les champs texte
            if widget_type in [forms.TextInput, forms.EmailInput, forms.PasswordInput]:
                field.widget.attrs['placeholder'] = f"Saisir {field.label.lower()}"


# ============================================================
# ✅ NOUVEAU : Formulaire pour les images du véhicule
# ===========================================================
class VehiculeImageForm(forms.ModelForm):
    class Meta:
        model = VehiculeImage
        fields = ['image', 'alt_text', 'ordre', 'est_principale']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'alt_text': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Description de l\'image (SEO)'}),
            'ordre': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'min': 0}),
            'est_principale': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
        }
        
# ============================================================
# ✅ FORMSET : Permet d'ajouter plusieurs images en même temps
# ============================================================
VehiculeImageFormSet = inlineformset_factory(
    parent_model=Vehicul,         # Parent
    model=VehiculeImage,   # Child
    form=VehiculeImageForm,
    extra=10,                   # 10 champs d'upload vides par défaut
    can_delete=True,            # Permet de supprimer des images existantes
    min_num=1,                  # Minimum 1 image
    max_num=25,                 # Maximum 20 images par véhicule
    validate_min=True,
    validate_max=True,
    
)