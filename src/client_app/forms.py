from django import forms
from .models import Maintenance

class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = [
            'client',
            'vehicul',               # Si lié au catalogue KOZ
            'marque', 'modele', 'annee', 'immatriculation', 'kilometrage_actuel',
            'origine',
            'type_maintenance',
            'priorite',
            'date_prevue',
            'date_prochaine',
            'date_derniere',
            'kilometrage_prochain',
            'kilometrage_dernier',
            'montant_estime',
            'notes_client',
            'notes_technicien'
        ]
        
        widgets = {
            'client': forms.Select(attrs={'class': 'select select-bordered w-full text-sm bg-white'}),
            'vehicul': forms.Select(attrs={'class': 'select select-bordered w-full text-sm bg-white'}),
            'marque': forms.TextInput(attrs={'class': 'input input-bordered w-full text-sm bg-white', 'placeholder': 'ex: Toyota'}),
            'modele': forms.TextInput(attrs={'class': 'input input-bordered w-full text-sm bg-white', 'placeholder': 'ex: Land Cruiser'}),
            'annee': forms.NumberInput(attrs={'class': 'input input-bordered w-full text-sm bg-white', 'placeholder': '2022'}),
            'immatriculation': forms.TextInput(attrs={'class': 'input input-bordered w-full text-sm bg-white uppercase', 'placeholder': 'ex: 11-JJ-4567'}),
            'kilometrage_actuel': forms.NumberInput(attrs={'class': 'input input-bordered w-full text-sm bg-white', 'placeholder': 'ex: 120000'}),
            'origine': forms.Select(attrs={'class': 'select select-bordered w-full text-sm bg-white'}),
            'type_maintenance': forms.Select(attrs={'class': 'select select-bordered w-full text-sm bg-white'}),
            'priorite': forms.Select(attrs={'class': 'select select-bordered w-full text-sm bg-white'}),
            'date_prevue': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'input input-bordered w-full text-sm bg-white'}),
            'date_prochaine': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'input input-bordered w-full text-sm bg-white'}),
            'date_derniere': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'input input-bordered w-full text-sm bg-white'}),
            'kilometrage_prochain': forms.NumberInput(attrs={'class': 'input input-bordered w-full text-sm bg-white', 'placeholder': 'ex: 130000'}),
            'kilometrage_dernier': forms.NumberInput(attrs={'class': 'input input-bordered w-full text-sm bg-white', 'placeholder': 'ex: 110000'}),
            'montant_estime': forms.NumberInput(attrs={'class': 'input input-bordered w-full text-sm bg-white', 'placeholder': 'Montant en FCFA'}),
            'notes_client': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full text-sm bg-white', 'rows': 3, 'placeholder': 'Remarques ou précisions particulières...'}),
            'notes_technicien': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full text-sm bg-white', 'rows': 3, 'placeholder': 'Remarques ou précisions particulières...'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_prevue'].required = True
        #Si vehicul est séléctionné, on peut pré-remplir marque/modele/annee
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'input input-bordered w-full text-sm bg-white'
                
        if self.instance and self.instance.vehicul:
            self.fields["marque"].initial = self.instance.vehicul.marque.nom
            self.fields["modele"].initial = self.instance.vehicul.modele
            self.fields["annee"].initial =  self.instance.vehicul.annee
                
    def clean(self):
        cleaned_data = super().clean()
        origine = cleaned_data.get("origine")
        vehicul = cleaned_data.get("vehicul")
        marque = cleaned_data.get("marque")
        modele = cleaned_data.get("modele")
        
        if origine == 'koz' and not vehicul:
            raise forms.ValidationError("Pour un vehicule acheté chez KOZ, Veillez séléctionner le modèle dans la liste")
        
        if origine == "externe" and (not marque or not modele):
            raise forms.ValidationError("Veillez indiquer la marque et le modèle du véhicule.")
        
        return cleaned_data
        
