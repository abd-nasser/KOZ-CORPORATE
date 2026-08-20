# leads_app/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import demande_financement, Vente
from client_app.models import Documents


from django import forms
from .models import Vente

class VenteSimpleForm(forms.ModelForm):
    class Meta:
        model = Vente
        fields = ["client", "vehicul", "montant"]
        labels = {
            "client": "Client acheteur",
            "vehicul": "Véhicule à vendre",
            "montant": "Montant de la vente",
        }
        widgets = {
            "client": forms.Select(attrs={
                "class": "select select-bordered w-full bg-white font-normal focus:border-blue-600 focus:outline-none"
            }),
            "vehicul": forms.Select(attrs={
                "class": "select select-bordered w-full bg-white font-normal focus:border-blue-600 focus:outline-none"
            }),
            "montant": forms.NumberInput(attrs={
                "class": "input input-bordered w-full bg-white focus:border-blue-600 focus:outline-none",
                "placeholder": "Ex: 12500000",
                "min": "0",
                "step": "500",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['montant'].required = True
        self.fields['vehicul'].required = True
        self.fields['client'].required =  True
        # Libellés par défaut pour les menus déroulants
        if "client" in self.fields:
            self.fields["client"].empty_label = "-- Choisir un client --"
        if "vehicul" in self.fields:
            self.fields["vehicul"].empty_label = "-- Choisir un véhicule --"
        
    
##POUR LE CLIENT
class DemandeFinancementForm(forms.ModelForm):
    #champs pour simulateur de credit 
    mensualite_souhaitee = forms.DecimalField(
        max_digits=12,
        decimal_places=0,
        required=False,
        label="💸 Mensualité souhaitée (FCFA)",
        widget=forms.NumberInput(attrs={
            "class": "input input-bordered w-full",
            'placeholder': 'Entrez la mensualité souhaitée (FCFA)',
            'hx-get':'/leads/estimer-prix/',                    #URL de la vue qui traite la simulation
            'hx-target': '#resultat-simulation',                #ID de l'élément où afficher le résultat de la simulation
            'hx-trigger': 'keyup changed delay:300ms',          #Déclenche la requête après 300ms de pause dans la saisie
            'hx-include': "#simulation-fields" ,                 #Inclure les champs du formulaire dans la requête HTMX
        })
    )
    
    taux_interet = forms.ChoiceField(
        choices = [(i, f"{i}%") for i in range(0, 18)],  # Taux d'intérêt de 0% à 17%
        required=False,
        initial=8,  # Taux d'intérêt par défaut (exemple : 8%)
        label="📈 Taux d'intérêt annuel (%)",
        widget=forms.Select(attrs={
            "class": "select select-bordered w-full",
            'hx-get':'/leads/estimer-prix/', # URL de la vue qui traite la simulation
            'hx-target': '#resultat-simulation',                # ID de l'élément où afficher le résultat de la simulation
            'hx-trigger': 'change delay:300ms',                   # Déclenche la requête au changement de sélection
            'hx-include': '#simulation-fields',                    # Inclure les champs du formulaire dans la requête HTMX
        })
    )
    
    
    class Meta:
        model = demande_financement
        fields = [
            'apport',
            'duree_mois',
            'revenus_mensuel',
        ]
        widgets = {
            'apport': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'step': 10000,
                'placeholder': 'Montant de l’apport (FCFA)'
            }),
            'duree_mois': forms.Select(choices=[
                (12, '12 mois'),
                (24, '24 mois'),
                (36, '36 mois'),
                (48, '48 mois'),
                (60, '60 mois'),
            ], attrs={'class': 'select select-bordered w-full'}),
            
            'revenus_mensuel': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'step': 50000,
                'placeholder': 'Revenus mensuels (FCFA)'
            }),
        }

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    
    
    def clean(self):
        cleaned_data = super().clean()
        apport = cleaned_data.get('apport')
        revenus = cleaned_data.get('revenus_mensuel')
        
        if apport is None or apport <= 0:
            raise forms.ValidationError("L'apport ne peut pas être négatif.")
        if revenus is  None or revenus <= 0:
            raise forms.ValidationError("Les revenus ne peuvent pas être négatifs")
        return cleaned_data

  
#POUR LE COMMERCIAL
class GestionFinancementForm(forms.ModelForm):
    class Meta:
        model = demande_financement
        fields = [
            "financement_type","financement_par",
            "notes_commercial", 
        ]  
                
        widgets= {
            "financement_type":forms.Select(attrs={"class":"select select-bordered"}),
            "financement_par": forms.Select(attrs={"class":"select select-bordered"}),
            "notes_commercial":forms.Textarea(attrs={"class":"input input-bordered"}),
            
        }


class DocumentsUploadForm(forms.ModelForm):
    """
    Formulaire d'upload de documents avec validation :
    - Taille max : 100MB
    - Formats autorisés : JPG, PNG, PDF, HEIC, XLSX
    - Vérification des documents obligatoires
    """
    
    class Meta:
        model = Documents
        fields = [
            'cni_passeport',
            'justificatif_domicile',
            'attestation_non_engagement',
            'contrat_travail',
            'attestation_travail',
            'quittance_salaire',      
            'bulletin_1',
            'bulletin_2',
            'bulletin_3',
            'relevé_bancaire',
            'specimen_signature',
            'certificat_presence',
            'geolocalisation',
            'garanties',
            'recu_acompte',
            'fiche_demande',
        ]
        
        # Widgets pour styliser les champs de fichier
        widgets = {
            field: forms.ClearableFileInput(attrs={'class': 'file-input file-input-bordered w-full'})
            for field in fields
        }
    
    # === CONSTANTES DE VALIDATION ===
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 Mo (100 millions d'octets)
    ALLOWED_TYPES = [
         # Images
        'image/jpeg',                      # .jpg, .jpeg
        'image/png',                       # .png
        'application/pdf',                 # .pdf
        'image/heic',                      # .heic (iPhone)
        
         # 👇 Documment WORD ET EXEL
        'application/msword',              # .doc (ancien Word)
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
    ]
    
    ALLOWED_EXTENSIONS = [
        '.jpg', '.jpeg', '.png', '.pdf', '.heic', '.xlsx',
        '.doc', '.docx',  # 👈 Ajoute les extensions Word
    ]
    
    def clean(self):
        """
        Méthode principale de validation.
        S'exécute après les validations individuelles des champs.
        """
        cleaned_data = super().clean()
        
        # === 1. VALIDATION DES CHAMPS OBLIGATOIRES ===
        missing_docs = []
        required_fields = [
            ('cni_passeport', 'CNI / Passeport'),
            ('justificatif_domicile', 'Justificatif de domicile'),
            ('attestation_non_engagement', 'Attestation de non-engagement'),
            ('contrat_travail', 'Contrat de travail'),
            ('attestation_travail', 'Attestation de travail (<3 mois)'),
            ('bulletin_1', 'Bulletin de paie (mois -3)'),
            ('bulletin_2', 'Bulletin de paie (mois -2)'),
            ('bulletin_3', 'Bulletin de paie (mois -1)'),
            ('relevé_bancaire', 'Relevé bancaire (12 mois) + RIB'),
            ('specimen_signature', 'Spécimen de signature'),
            ('quittance_salaire', 'Quittance de salaire'),
        ]
        
        for field_name, field_label in required_fields:
            if not cleaned_data.get(field_name): 
                missing_docs.append(field_label)
        
        if missing_docs:
            raise forms.ValidationError(
                f"Documents obligatoires manquants : {', '.join(missing_docs)}"
            )
        
        # === 2. VALIDATION DES FICHIERS (taille, type, extension) ===
        for field_name, file_obj in self.files.items():
            # === 2a. Vérification taille (max 100MB) ===
            if file_obj.size > self.MAX_FILE_SIZE:
                self.add_error(
                    field_name,
                    f"Le fichier '{file_obj.name}' est trop volumineux. "
                    f"Taille max : 100MB (actuel : {file_obj.size // (1024*1024)}MB)"
                )
                continue  # On passe au fichier suivant
            
            # === 2b. Vérification du type MIME ===
            if file_obj.content_type not in self.ALLOWED_TYPES:
                self.add_error(
                    field_name,
                    f"Type de fichier non supporté pour '{file_obj.name}'. "
                    f"Formats autorisés : JPG, PNG, PDF, HEIC, XLSX"
                )
                continue
            
            # === 2c. Vérification de l'extension ===
            import os
            file_extension = os.path.splitext(file_obj.name)[1].lower() #ex os.path.splitext(file_obj.name) = ["document", ".pdf"][1] = '.pdf'
            if file_extension not in self.ALLOWED_EXTENSIONS:
                self.add_error(
                    field_name,
                    f"Extension non autorisée pour '{file_obj.name}'. "
                    f"Extensions autorisées : {', '.join(self.ALLOWED_EXTENSIONS)}"
                )
        
        return cleaned_data
    
    def clean_cni_passeport(self):
        """Validation spécifique pour le champ CNI/Passeport"""
        file = self.cleaned_data.get('cni_passeport')
        
        # ✅ Si le champ est vide, on ne fait rien (la validation des champs obligatoires s'en chargera)
        if not file:
            return file
        
        # ✅ Maintenant on peut valider le type
        content_type = getattr(file, 'content_type', None)
        
        if content_type and content_type not in ['image/jpeg', 'image/png']:
            raise forms.ValidationError(
                f"La CNI/Passeport doit être une image (JPG ou PNG). Type détecté : {content_type}"
            )
        
        # Fallback si content_type est None (cas rare)
        if not content_type:
            import os
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png']:
                raise forms.ValidationError(
                    "La CNI/Passeport doit être une image (JPG ou PNG)"
                )
        
        return file