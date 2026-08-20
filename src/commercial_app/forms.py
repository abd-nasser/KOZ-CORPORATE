from django import forms
from .models import Offre

class OffreFinancementForm(forms.ModelForm):
    class Meta:
        model = Offre
        fields = [
            'vehicule_propose',
            'prix_vehicule',
            'apport_demande',
            'duree_mois',
            'taux_interet',
            'frais_dossier',
            'frais_garantie',
            'financement_type',
            'financement_par',
            'date_expiration'
        ]
        widgets = {
            'vehicule_propose': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'prix_vehicule': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            'apport_demande': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            # 'duree_mois' PAS de widget ici → Django utilise le select par défaut avec les choices
            'taux_interet': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            'frais_dossier': forms.NumberInput(attrs={'class': 'input input-bordered w-full',}),
            'frais_garantie': forms.NumberInput(attrs={'class': 'input input-bordered w-full',}),
            'financement_type': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'financement_par' : forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'date_expiration': forms.DateInput(attrs={'class': 'input input-bordered w-full', 'type': 'date'}),
            
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['duree_mois'].choices = [(12, '12 mois'), (24, '24 mois'), (36, '36 mois'), (48, '48 mois'), (60, '60 mois')]
        self.fields['duree_mois'].widget.attrs.update({'class': 'select select-bordered w-full'})
        self.fields['vehicule_propose'].required = True
        
        

class OffreSimpleForm(forms.ModelForm):
    """Formulaire pour l'offre de financement (UNIQUEMENT 3 champs)"""
    
    class Meta:
        model = Offre
        fields = [
            "vehicule_propose", 
            "montant_propose", 
            "date_expiration"
        ]  # ← Seulement ces 3 champs !
        
        widgets = {
            'vehicule_propose': forms.Select(attrs={
                'class': 'input input-bordered w-full',
            }),
            'montant_propose': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'step': '1000',
                'placeholder': 'Montant de l\'offre',
            }),
            'date_expiration': forms.DateTimeInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'datetime-local',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre les champs obligatoires (si nécessaire)
        self.fields['vehicule_propose'].required = True
        self.fields['montant_propose'].required = True
        self.fields['date_expiration'].required = True