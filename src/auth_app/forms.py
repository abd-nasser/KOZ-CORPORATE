# auth_app/forms.py

from django import forms
from .models import kozUser
from django.core.mail import send_mail
from koz_flow.tasks import send_email_task
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib import messages
import secrets
import string
import logging


logger = logging.getLogger(__name__)

import secrets
import string
from django import forms
from .models import kozUser  # Adapte le chemin selon ton projet


import secrets
import string
from django import forms
from .models import kozUser  # Adapte le chemin selon ton projet


class UserRegisterForm(forms.ModelForm):
    """Formulaire de création d'utilisateur pour le directeur / commercial"""

    class Meta:
        model = kozUser
        fields = [
            'email',
            'nom_complet',
            'telephone',
            'adresse',
            'role',
            'profession_choisie',
            'profession',
            'genre',
            'pays',
            'ville',
            'assigned_commercial',
        ]

        widgets = {
            'email': forms.EmailInput(
                attrs={'class': 'input input-bordered w-full'}
            ),
            'nom_complet': forms.TextInput(
                attrs={'class': 'input input-bordered w-full'}
            ),
            'telephone': forms.TextInput(
                attrs={'class': 'input input-bordered w-full'}
            ),
            'adresse': forms.Textarea(
                attrs={'class': 'textarea textarea-info w-full', 'rows': 3}
            ),
            'role': forms.Select(
                attrs={'class': 'select select-bordered w-full'}
            ),
        }

    def __init__(self, *args, **kwargs):
        # Récupère l'utilisateur connecté depuis la View grâce à get_form_kwargs
        self.created_by = kwargs.pop("created_by", None)

        super().__init__(*args, **kwargs)

        if self.created_by and not self.created_by.is_superuser:
            self.fields["role"].choices = [
                ('client', "Client"),
            ]

        # Filtre la liste des commerciaux assignables
        if 'assigned_commercial' in self.fields:
            self.fields['assigned_commercial'].queryset = (
                kozUser.objects.filter(role='commercial')
            )

        # Configuration des classes CSS pour chaque type de champ
        config = {
            forms.TextInput: 'input input-bordered w-full',
            forms.EmailInput: 'input input-bordered w-full',
            forms.PasswordInput: 'input input-bordered w-full',
            forms.Select: 'select select-bordered w-full',
            forms.CheckboxInput: 'checkbox checkbox-info',
            forms.Textarea: 'textarea textarea-info w-full',
        }

        for field_name, field in self.fields.items():
            widget_type = type(field.widget)
            css_class = config.get(widget_type, 'input input-bordered w-full')
            field.widget.attrs['class'] = css_class

            # Ajoute un placeholder pour les champs texte
            if widget_type in [
                forms.TextInput,
                forms.EmailInput,
                forms.PasswordInput,
            ]:
                label_text = field.label.lower() if field.label else field_name
                field.widget.attrs['placeholder'] = f"Saisir {label_text}"

    def save(self, commit=True):
        user = super().save(commit=False)

        # Génération du mot de passe temporaire
        alphabet = string.ascii_letters + string.digits
        raw_password = ''.join(secrets.choice(alphabet) for _ in range(10))

        # Attribution des droits staff pour les rôles d'administration
        if user.role in ["directeur", "commercial"]:
            user.is_staff = True

        user.set_password(raw_password)

        # 🔑 ATTRIBUTION DU MOT DE PASSE EN CLAIR À L'INSTANCE
        # Permet à la Vue / Celery de lire le mot de passe temporaire généré
        user.raw_password = raw_password

        if (
            user.role == "client"
            and self.created_by
            and self.created_by.role == "commercial"
        ):
            user.assigned_commercial = self.created_by

        if commit:
            user.save()

        return user
            

class ChangePasswordForm(forms.Form):
    
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "input input-bordered"}),
        label="Email"
        )
    
    current_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "input input-bordered"}
            ),
        label="Mot de passe actuel",
        required=True
        )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "input input-bordered"}),
        required=True,
        label="Nouveau mot de passe"
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "input input-bordered"}),
        required=True,
        label="Confirmez Nouveau mot de passe",
    )
    
  
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
    
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        current_password = cleaned_data.get("current_password")
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if not self.user:
            raise forms.ValidationError("Utilisateur Introuvable")
        
        if self.user.email != email:
            raise forms.ValidationError("l'adresse mail est incorrect")
        
        if not self.user.check_password(current_password):
            raise forms.ValidationError("Le Mot de passe actuel est incorrect")
        
        if new_password and new_password != confirm_password :
            raise forms.ValidationError("Les mot de passe ne correspondent pas")
        
        if len(new_password)<6:
            raise forms.ValidationError('le mot de passe doit contenir au moin 6 caractère')
        
        # Vérifie que le nouveau mot de passe est différent de l'ancien
        if current_password == new_password:
            raise forms.ValidationError("Le nouveau mot de passe doit être différent de l'ancien")
        
        return cleaned_data
    
    

    

        