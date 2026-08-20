from django import forms

from .models import Actualite, AvisReseau, VideoTemoignage, Temoignage


class TemoignageTextuelForm(forms.ModelForm):
    class Meta:
        model = Temoignage
        fields = ['nom', 'prenom', 'photo', 'message', 'note']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control input input-bordered'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control input input-bordered'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control-file file-input file-input-bordered'}),
            'message': forms.Textarea(attrs={'rows': 4, 'class': 'form-control textarea textarea-bordered'}),
            'note': forms.Select(attrs={'class': 'form-control select select-bordered'}),
            'source': forms.Select(attrs={'class': 'form-control select select-bordered'}),
            'est_approuve': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'est_vedette': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AvisReseauForm(forms.ModelForm):
    class Meta:
        model = AvisReseau
        fields = [
            'reseau',
            'nom_utilisateur',
            'message',
            'date_publication',
            'image',
            'lien',
            'est_actif',
        ]
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'class': 'form-control textarea textarea-bordered'}),
            'date_publication': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control input-border'}),
            'reseau': forms.Select(attrs={'class': 'form-control select select-bordered'}),
            'nom_utilisateur': forms.TextInput(attrs={'class': 'form-control input input-bordered'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control file-input file-input-bordered'}),
            'lien': forms.URLInput(attrs={'class': 'form-control input input-bordered'}),
            'est_actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class VideoTemoignageForm(forms.ModelForm):
    class Meta:
        model = VideoTemoignage
        fields = [
            'titre',
            'description',
            'video_file',
            'video_url',
            'embed_code',
            'duree',
            'est_actif',
            'ordre',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'embed_code': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'duree': forms.NumberInput(attrs={'class': 'input input-bordered'}),
            'ordre': forms.NumberInput(attrs={'class': 'input input-bordered'}),
            'titre': forms.TextInput(attrs={'class': 'input input-bordered '}),
            'video_file': forms.ClearableFileInput(attrs={'class': 'form-control file-input file-input-bordered'}),
            'video_url': forms.URLInput(attrs={'class': 'input input-bordered'}),
            
        }


class ActualiteForm(forms.ModelForm):
    class Meta:
        model = Actualite
        fields = [
            'titre',
            'sous_titre',
            'description',
            'description_courte',
            'type',
            'image_principale',
            'image_1',
            'image_2',
            'image_3',
            'image_4',
            'image_5',
            'video_file',
            'video_url',
            'lien_externe',
            'lien_interne',
            'date_evenement',
            'date_publication',
            'date_fin',
            'est_publie',
            'est_vedette',
            'ordre',
        ]
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'sous_titre': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'textarea textarea-bordered w-full'}),
            'description_courte': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'type': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'image_principale': forms.ClearableFileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'image_1': forms.ClearableFileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'image_2': forms.ClearableFileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'image_3': forms.ClearableFileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'image_4': forms.ClearableFileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'image_5': forms.ClearableFileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'video_file': forms.ClearableFileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'video_url': forms.URLInput(attrs={'class': 'input input-bordered w-full'}),
            'lien_externe': forms.URLInput(attrs={'class': 'input input-bordered w-full'}),
            'date_evenement': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'input input-bordered w-full'}),
            'date_publication': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'input input-bordered w-full'}),
            'date_fin': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'input input-bordered w-full'}),
            'ordre': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            'est_publie': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'est_vedette': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'lien_interne': forms.URLInput(attrs={'class': 'input input-bordered w-full'}),
        }
