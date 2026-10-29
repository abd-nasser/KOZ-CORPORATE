# `path` declare les URL Django et `reverse_lazy` résout une URL nommée sans attendre le chargement complet des routes.
from django.urls import path, reverse_lazy
# Les vues d'authentification Django fournissent le formulaire, le jeton et les écrans du reset sans jeton maison.
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from chat_app import views
from .views import (ApiRegisterView, LoginView, 
                    MeView, LogoutView, site_user_register,
                    UserRegisterView, ChangePasswordView, login_page, login_simple, logout_simple_sur_home_page, logout_sur_ERP)

app_name = "auth_app"

urlpatterns = [
    
    #path("", views.home_page_view, name="home-page")
    path("interface/connexion", login_page, name="interface-login-page"),
    
    # Inscription
    path('register/', ApiRegisterView.as_view(), name='register'),
    path('site-register/', site_user_register, name='site-register'),
    # → http://127.0.0.1:8000/api/auth/register/
    # → http://127.0.0.1:8000/api/auth/site-register/
    
    #Connexion
    path('login/', LoginView.as_view(), name='login'),
    # → http://127.0.0.1:8000/api/auth/login/
    
    #Utilisateur connecté
    path('me/', MeView.as_view(), name="Me-view"),
    # → http://127.0.0.1:8000/api/auth/me/
    
    #Déconnexion
    path('logout/', LogoutView.as_view(), name="logout"),
    # → http://127.0.0.1:8000/api/auth/logout/
    
    # Rafraîchir le token (obtenir un nouveau access token avec le refresh token)
    path('token/refresh/', TokenRefreshView.as_view(), name='Token_refresh'),
    # → http://127.0.0.1:8000/api/auth/token/refresh/
    
    
    
    #-------------------------ERP  URLS-------------------
    #-------------------------ERP  URLS-------------------
    path("Userregister/",UserRegisterView.as_view(), name="user-register"),
    path("change_password/",ChangePasswordView.as_view(), name="change-password"),
    path("login/simple/", login_simple, name="login-simple"),
    path("logout/simple/", logout_simple_sur_home_page, name="logout-simple-sur-home-page"),
    path('logout/sur/ERP', logout_sur_ERP, name="logout-sur-erp" ),
    
    # Cette route reçoit l'adresse e-mail et demande à Django d'envoyer le lien de réinitialisation.
    path(
        # Le chemin public commence par password-reset/ sous le préfixe /api/auth/ de ce fichier de routes.
        "password-reset/",
        # PasswordResetView ne crée un lien que pour un compte actif ayant un mot de passe utilisable.
        auth_views.PasswordResetView.as_view(
            # Le template partagé gère trois rendus: formulaire, lien invalide et confirmation sans formulaire.
            template_name="auth_templates/password_reset_page.html",
            
            # Ce template texte contient le lien sécurisé inclus dans le message.
            email_template_name="auth_templates/password_reset_email.txt",
            
            # Django rend ce template comme sujet du courriel.
            subject_template_name="auth_templates/password_reset_subject.txt",
            
            # Après la demande, le navigateur arrive sur l'écran de confirmation neutre.
            success_url=reverse_lazy("auth_app:password_reset_done"),
            
            # Ce contexte fournit le titre et le texte propres à l'étape de demande.
            extra_context={
                # Titre affiché au-dessus du champ e-mail.
                "page_title": "Mot de passe oublié",
                # Instruction visible avant l'envoi du formulaire.
                "page_message": "Saisissez l'adresse e-mail associée à votre compte.",
            },
        ),
        # Ce nom permet aux templates et au code Python de construire l'URL sans la coder en dur.
        name="password_reset",
    ),
    # Cette route confirme la demande sans dire si l'adresse saisie existe dans la base.
    path(
        # Ce chemin est la destination après l'envoi du formulaire de demande.
        "password-reset/done/",
        # PasswordResetDoneView affiche simplement la confirmation, sans exposer l'existence du compte.
        auth_views.PasswordResetDoneView.as_view(
            # Le template affiche la confirmation sans formulaire grâce aux messages fournis ci-dessous.
            template_name="auth_templates/password_reset_page.html",
            # Le message reste identique pour une adresse connue ou inconnue afin d'éviter l'énumération de comptes.
            extra_context={
                # Titre visible sur l'écran de confirmation.
                "page_title": "Vérifiez votre boîte e-mail",
                # La formulation conditionnelle ne révèle jamais si un compte correspond.
                "page_message": "Si un compte correspond à cette adresse, un lien de réinitialisation vient de vous être envoyé.",
            },
        ),
        # Ce nom est utilisé comme destination après la soumission du formulaire d'e-mail.
        name="password_reset_done",
    ),
    
    # Cette route valide l'identifiant et le jeton reçus dans le lien du courriel.
    path(
        # uidb64 identifie l'utilisateur sans exposer directement son identifiant numérique; token est signé et temporaire.
        "reset/<uidb64>/<token>/",
        # PasswordResetConfirmView vérifie le jeton et enregistre le nouveau mot de passe de façon sécurisée.
        auth_views.PasswordResetConfirmView.as_view(
            # Le template partagé distingue le formulaire de nouveau mot de passe du lien invalide.
            template_name="auth_templates/password_reset_page.html",
            # Un jeton valide amène l'utilisateur sur la confirmation finale.
            success_url=reverse_lazy("auth_app:password_reset_complete"),
            # Ces textes adaptent l'en-tête du template à la saisie du nouveau mot de passe.
            extra_context={
                # Titre de l'étape de confirmation du lien.
                "page_title": "Choisir un nouveau mot de passe",
                # Instruction donnée avant la saisie du nouveau mot de passe.
                "page_message": "Définissez un nouveau mot de passe pour votre compte.",
            },
        ),
        # Ce nom est utilisé dans le lien du courriel et pour les redirections.
        name="password_reset_confirm",
    ),
    # Cette dernière route confirme que le mot de passe a bien été modifié.
    path(
        # Le chemin ne contient plus de jeton car celui-ci a déjà été validé.
        "reset/complete/",
        # PasswordResetCompleteView affiche l'état final sans traiter de formulaire.
        auth_views.PasswordResetCompleteView.as_view(
            # Le template partagé affiche la confirmation finale sans formulaire.
            template_name="auth_templates/password_reset_page.html",
            # Le contexte remplace les textes génériques du template.
            extra_context={
                # Titre de succès affiché après l'enregistrement.
                "page_title": "Mot de passe modifié",
                # Invite l'utilisateur à retourner sur la page de connexion.
                "page_message": "Votre nouveau mot de passe est enregistré. Vous pouvez maintenant vous connecter.",
            },
        ),
        # Ce nom sert de destination après la modification du mot de passe.
        name="password_reset_complete",
    ),
]
