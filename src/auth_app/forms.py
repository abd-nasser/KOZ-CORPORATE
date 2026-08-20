# auth_app/forms.py

from django import forms
from .models import kozUser
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib import messages
import secrets
import string
import logging


logger = logging.getLogger(__name__)

class UserRegisterForm(forms.ModelForm):
    """Formulaire de création d'utilisateur pour le directeur"""
    
    class Meta:
        model = kozUser
        fields = ['email', 'nom_complet', 'telephone', 'adresse', 
                  'role', "profession_choisie", 
                  "profession", "genre", "pays", "ville", 
                  "assigned_commercial"]
        
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'input input-bordered w-full'}),
            'nom_complet': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'telephone': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'adresse': forms.Textarea(attrs={'class': 'textarea textarea-info w-full', 'rows': 3}),
            'role': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            
        }
    
    def __init__(self, *args, **kwargs):
        #Récupère l'utilisateur connecter depuis la View grace à la methode get_form_kwargs
        
        # On sort created_by du dictionnaire
        self.created_by = kwargs.pop("created_by", None)
        
        # Maintenant kwargs n'a PLUS created_by
        super().__init__(*args, **kwargs)
        
        if self.created_by and not self.created_by.is_superuser:
            self.fields["role"].choices = [
                ('client', "Client"),
                # ('directeur', 'Directeur'), ← caché
                # ('commercial', 'Commercial'), ← caché
                ]
        # Filtre la liste des commerciaux assignables
        if 'assigned_commercial' in self.fields:
            self.fields['assigned_commercial'].queryset = kozUser.objects.filter(role='commercial')
                  
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
            # Récupère la classe selon le type du widget
            widget_type = type(field.widget)
            css_class = config.get(widget_type, 'input input-bordered w-full')
            field.widget.attrs['class'] = css_class
            
            # Ajoute un placeholder pour les champs texte
            if widget_type in [forms.TextInput, forms.EmailInput, forms.PasswordInput]:
                field.widget.attrs['placeholder'] = f"Saisir {field.label.lower()}"

                 
    def save(self, commit = True):
        user = super().save(commit=False)
        
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(10))
        
         # Si c'est un directeur ou commercial, donne les droits staff
        if user.role in ["directeur", "commercial"]:
            user.is_staff = True

  
        user.set_password(password)    
        
        if user.role == "client" and self.created_by and self.created_by.role == "commercial":
            user.assigned_commercial = self.created_by
                 

        if commit:
            user.save()
           
        try:
            context_email = {
                                'new_user': user.nom_complet,
                                'email': user.email,
                                'password_temporaire':password,
                                'link_espace_de_connexion': "https://koz-corporate.pro/api/auth/interface/connexion"
                                }
            html_message = render_to_string('emails/auth/identifiant_user.html', context_email)
            plain_message = strip_tags(html_message)                   
            send_mail(
                subject="Vos identifiants KOZ Services",
                message=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,  # Si False, l'erreur remonte
            )
            
        except Exception as e:
            # L'utilisateur est créé mais l'email n'a pas été envoyé
            logger.error(f"{e}--Erreur lors d'envoie de l'email")
        
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
    
    

    

        