from django import forms
from .models import Offre
from home_app.models import RendezVous

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
        
        
class RdvForm(forms.ModelForm):
    class Meta:
        model = RendezVous
        fields = ['client', 'nom', 'prenom', 'telephone', 'date_rendez_vous', 'duree', 'motif']
        widgets = {
            'date_rendez_vous': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'input input-bordered w-full'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'client': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'nom': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Nom du prospect'}),
            'prenom': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Prénom'}),
            'telephone': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Téléphone'}),
            'duree': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'min': '15', 'step': '15'}),
            'motif': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Ex: Essai véhicule / Signature contrat'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optionnel : filtrer uniquement les utilisateurs ayant le rôle client si applicable
        self.fields['client'].required = False
        self.fields['nom'].required = False
        self.fields['prenom'].required = False
        self.fields['telephone'].required = False
        self.fields['client'].empty_label = "-- Sélectionner un client existant (Optionnel) --"

    def clean(self):
        cleaned_data = super().clean()
        client = cleaned_data.get('client')
        nom = cleaned_data.get('nom')
        telephone = cleaned_data.get('telephone')

        # 🛡️ Règle de validation : Client en BDD OU (Nom + Téléphone)
        if not client and not (nom and telephone):
            raise forms.ValidationError(
                "Veuillez soit sélectionner un client existant, soit renseigner le Nom et le Téléphone du prospect."
            )
        return cleaned_data
    
    

class ClientRdvForm(forms.ModelForm):
    class Meta:
        model = RendezVous
        fields = [ 'date_rendez_vous', 'duree', 'motif']
        widgets = {
            'date_rendez_vous': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'input input-bordered w-full'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            
            'duree': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'min': '15', 'step': '15'}),
            'motif': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Ex: Essai véhicule / Signature contrat'}),
        }
