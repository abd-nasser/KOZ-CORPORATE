from email import header
import time

from django.shortcuts import render, redirect
from django.contrib.auth import(
                                authenticate, 
                                login as django_login, 
                                logout as django_logout) 
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import update_session_auth_hash

from django.core.mail import send_mail
from koz_flow.tasks import send_email_task
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.conf import settings
from django.urls import reverse_lazy, reverse
from django.utils import timezone

from django.contrib import messages
from django.views.generic import(
    TemplateView, ListView, CreateView, FormView,
    UpdateView, DeleteView, DetailView
)

from django.contrib.auth.mixins import(
    LoginRequiredMixin, UserPassesTestMixin
)

from rest_framework import status #status = codes HTTP(200 = OK, 400 = Erreur, 500 = erreu server)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken



from .serializers import RegisterSerializers, UserSerializer
from .forms import UserRegisterForm, ChangePasswordForm
from .models import kozUser
from directeur_app.views import DirecteurDashboardView
from commercial_app.views import CommercialDashboardView


import logging

logger = logging.getLogger(__name__)



def login_page(request):
    
    """
    Affiche la page de connexion HTML
    C'est une vue Django classique, pas une API
    """
    return render(request, "auth_templates/login.html")   


import logging
from django.conf import settings
from django.db import transaction
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from koz_flow.tasks import send_email_task  # Adapte le chemin d'import selon ton projet


logger = logging.getLogger(__name__)


def site_user_register(request):
    """
    Crée un compte utilisateur depuis le site et affiche le résultat dans un partial HTMX.
    """
    if request.method != 'POST':
        return redirect('home_app:home-page')

    email = request.POST.get('email', '').strip()
    nom_complet = request.POST.get('nom_complet', '').strip()
    telephone = request.POST.get('telephone', '').strip()
    adresse = request.POST.get('adresse', '').strip()
    pays = request.POST.get('pays', '').strip()
    ville = request.POST.get('ville', '').strip()
    genre = request.POST.get('genre', '').strip() or None
    profession = request.POST.get('profession', '').strip()
    password = request.POST.get('password', '')
    password2 = request.POST.get('password2', '')

    # Helper interne pour homogénéiser et simplifier le rendu des partials HTMX
    def render_register_response(context):
        response = render(request, 'partials/auth/register_result.html', context)
        response["HX-Trigger"] = "closeRegisterModal"
        return response

    # 🛑 1. VALIDATIONS CÔTÉ SERVEUR (Sorties précoces)
    if not email or not nom_complet or not telephone or not password or not password2 or not pays or not ville:
        return render_register_response({
            'success': False,
            'title': 'Inscription échouée',
            'message': 'Tous les champs obligatoires doivent être remplis.',
            'reload_on_close': False,
        })

    if password != password2:
        return render_register_response({
            'success': False,
            'title': 'Inscription échouée',
            'message': 'Les mots de passe ne correspondent pas.',
            'reload_on_close': False,
        })

    if len(password) < 6:
        return render_register_response({
            'success': False,
            'title': 'Inscription échouée',
            'message': 'Le mot de passe doit contenir au moins 6 caractères.',
            'reload_on_close': False,
        })

    if kozUser.objects.filter(email=email).exists():
        return render_register_response({
            'success': False,
            'title': 'Inscription échouée',
            'message': 'Un compte existe déjà avec cette adresse e-mail.',
            'reload_on_close': False,
        })

    try:
        # 🔴 2. TRANSACTION ATOMIQUE : Création de l'utilisateur
        with transaction.atomic():
            user = kozUser.objects.create_user(
                email=email,
                nom_complet=nom_complet,
                telephone=telephone,
                password=password,
                adresse=adresse,
                pays=pays,
                ville=ville,
                genre=genre,
                profession=profession,
                role='client',
                is_active=True,
            )

            # 🟢 3. PRÉPARATION DE L'EMAIL DE BIENVENUE
            context_email = {
                'user': user,
                'nom_complet': nom_complet,
                'url_espace_client': request.build_absolute_uri(reverse('client_app:client-view')),
            }
            html_message = render_to_string(
                'emails/auth/welcome_client.html', context_email
            )
            plain_message = strip_tags(html_message)

            # 🟢 4. ON_COMMIT : Tâche Celery déclenchée APRÈS validation SQL
            transaction.on_commit(
                lambda: send_email_task.delay(
                    subject="Bienvenue chez KOZ Services !",
                    plain_message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                )
            )

        # 🟢 5. Réponse HTMX de succès
        return render_register_response({
            'success': True,
            'title': 'Inscription réussie',
            'message': 'Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.',
            'reload_on_close': True,
        })

    except Exception as e:
        logger.error(f"Erreur lors de la création du compte site ({email}) : {e}")
        return render_register_response({
            'success': False,
            'title': 'Inscription échouée',
            'message': 'Impossible de créer votre compte pour le moment. Veuillez réessayer plus tard.',
            'reload_on_close': False,
        })

#------------- VUE POUR L'INSCRIPTION ----------------------
#APIView = une vue qui répond aux requetes GET, POST, PUT, DELETE
#@method_decorator(csrf_exempt, name='dispatch')
class ApiRegisterView(APIView):
    #Tout le monde peut s'inscrie
    permission_classes = [AllowAny]
    
    def post(self, request):
            #on recupère les donné envoyé par user
        try:
            serializer = RegisterSerializers(data=request.data)
            
            #si les données sont valide on creer user
            if serializer.is_valid():
                user = serializer.save()
                    
                # on actualise les tokens du user
                refresh = RefreshToken.for_user(user)
                    
                #Si tout est ok en renvoie une reponse en json
                return Response({
                        'utilisateur': RegisterSerializers(user).data, # on renvoie les données du user créé
                        'token': str(refresh), # on renvoie le token de rafraichissement
                        'acces': str(refresh.access_token), # on renvoie le token d'accès
                    }, status=status.HTTP_201_CREATED) # 201 = Créé avec succès
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) #
                
        except Exception as e:
            logger.error(f"Erreur lors de l'inscription: {str(e)}")
            return Response(
                    {"error":"Une erreur est survenue lors de l'inscription"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                                )
        
# ----- VUE POUR LA CONNEXION -----
#@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes= [AllowAny] # Tout le monde peut se connecter
    
    def post(self, request):
        #recupère l'email et le password
        try:
            email = request.data.get("email")
            password = request.data.get("password")

            
            user = authenticate(request, email=email, password=password) 
            
            if user is not None:
                
                django_login(request, user)
                refresh = RefreshToken.for_user(user)
                
                if user.is_superuser or user.role == "directeur":
                    redirect_url = request.build_absolute_uri(reverse("directeur_app:directeur-view"))
                    
                elif user.role == 'commercial':
                    redirect_url = request.build_absolute_uri(reverse("commercial_app:commercial-view"))
                
                else:
                    redirect_url = request.build_absolute_uri(reverse("client_app:client-view"))   
                
                # on renvoie la reponse avec les tokens et la redirection
                
                return Response( data={
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data,
        'redirect_url': redirect_url,
    },
    headers={
        'Access-Control-Allow-Origin': 'http://127.0.0.1:8000',
        'Access-Control-Allow-Credentials': 'true',
    },  # ← headers (au pluriel) pour permettre le partage de cookies entre les ports
    status=status.HTTP_200_OK) # 200 = OK
            else:
                # Si l'authentification a échoué (mauvais email ou mot de passe)
                return Response({"error":"Email ou mot de passe incorrect"},
                                status=status.HTTP_401_UNAUTHORIZED # 401 = Non autorisé
                                )
        except Exception as e:
            logger.error(f"Erreur lors de la connexion: {str(e)}")
            return Response({"error":"Une erreur est survenue lors de la connexion"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                            )

# ----- VUE POUR OBTENIR L'UTILISATEUR CONNECTÉ -----
class MeView(APIView):
    # IsAuthenticated = SEUL les utilisateurs connectés peuvent voir cette page
    # Si tu n'es pas connecté, Django renvoie une erreur 401 automatiquement
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
         # request.user = l'utilisateur qui a fait la requête (grâce au token JWT)
         # On le sérialise en JSON et on le renvoie
            return Response(UserSerializer(request.user).data)

# ----- VUE POUR LA DÉCONNEXION -----
class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        
        # 1️⃣ Blacklist du refresh token (si présent et valide)
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                message = "Déconnexion réussie (token blacklisté)"
            except Exception as e:
                logger.warning(f"Tentative de logout avec token invalide: {str(e)}")
                message = "Déconnexion réussie (token déjà expiré ou invalide)"
        else:
            message = "Déconnexion réussie (aucun token à blacklist)"
        
        # 2️⃣ ✅ TOUJOURS exécuter la déconnexion Django
        django_logout(request)
        print("logout reussi")
        print(f"is_authenticated: {request.user.is_authenticated}") 
        return Response({"message": message}, status=status.HTTP_200_OK)


#--------------------------LES Vus d'autentification pour ERP--------------------------
#---------------------------------------------------------------------------------------

import logging
from django.conf import settings
from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.generic import CreateView

from koz_flow.tasks import send_email_task  # Adapte le chemin selon ton projet


logger = logging.getLogger(__name__)


class UserRegisterView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = kozUser
    form_class = UserRegisterForm

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def get_template_names(self):
        if self.request.user.is_superuser or self.request.user.role == "directeur":
            return ["directeur_templates/directeur.html"]
        else:
            return ["commercial_templates/commercial.html"]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["created_by"] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            # 🔴 1. TRANSACTION ATOMIQUE : Création BDD
            with transaction.atomic():
                if self.request.user.role == 'commercial':
                    form.instance.role = 'client'
                    form.instance.is_active = True
                    form.instance.assigned_commercial = self.request.user

                user = form.save()  # `user.raw_password` contient le mot de passe en clair

                # 🟢 2. PRÉPARATION DU MAIL AVEC LES IDENTIFIANTS TEMPORAIRES
                context_email = {
                    'user': user,
                    'new_user': user.nom_complet,
                    'email': user.email,
                    'password_temporaire': getattr(user, 'raw_password', ''),
                    'link_espace_de_connexion': "https://koz-corporate.pro/api/auth/interface/connexion",
                }
                html_message = render_to_string(
                    'emails/auth/identifiant_user.html', context_email
                )
                plain_message = strip_tags(html_message)

                # 🟢 3. ON_COMMIT : Déclenchement de la tâche Celery
                transaction.on_commit(
                    lambda: send_email_task.delay(
                        subject="Vos identifiants KOZ Services",
                        plain_message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        html_message=html_message,
                    )
                )

            # 🟢 4. Réponse HTMX de succès
            response = render(
                self.request,
                'partials/auth/register_result.html',
                {
                    'success': True,
                    'title': f"Utilisateur {user.nom_complet} créé !",
                    'message': "📧 Les identifiants temporaires ont été envoyés par email.",
                    'reload_on_close': True,
                },
            )
            response["HX-Trigger"] = "closeRegisterModal"
            return response

        except Exception as e:
            logger.error(
                f"Erreur lors de la création d'utilisateur dans UserRegisterView: {e}"
            )
            response = render(
                self.request,
                'partials/auth/register_result.html',
                {
                    'success': False,
                    'title': "Création échouée",
                    'message': "Une erreur est survenue lors de la création de l'utilisateur.",
                    'reload_on_close': False,
                },
            )
            response["HX-Trigger"] = "closeRegisterModal"
            return response

    def form_invalid(self, form):
        return render(
            self.request,
            'partials/auth/_user_register_form_errors.html',
            {"user_register_form": form},
        )

def login_simple(request):
    """Gère la connexion simplifiée avec retours de partials HTMX."""
    if request.method != 'POST':
        return redirect("home_app:home-page")

    # Helper interne pour homogénéiser les réponses HTMX
    def render_login_response(context):
        response = render(request, "partials/auth/login_result.html", context)
        response["HX-Trigger"] = "closeLoginModal"
        return response

    try:
        email = (request.POST.get('email') or '').strip()
        password = request.POST.get('password') or ''

        if not email or not password:
            return render_login_response({
                'success': False,
                'title': 'Connexion impossible',
                'message': 'Veuillez renseigner votre email et votre mot de passe.',
                'reload_on_close': False,
            })

        user = authenticate(request, email=email, password=password)

        if user is None:
            return render_login_response({
                'success': False,
                'title': 'Email ou mot de passe incorrect',
                'message': 'Vérifiez vos identifiants et réessayez.',
                'reload_on_close': False,
            })

        # Connexion Django
        django_login(request, user)

        return render_login_response({
            'success': True,
            'title': f'Bienvenue, {user.nom_complet}',
            'message': 'Connexion réussie',
            'reload_on_close': True,
        })

    except Exception as e:
        logger.exception(f"Erreur lors de login_simple: {e}")
        return render_login_response({
            'success': False,
            'title': 'Erreur serveur',
            'message': 'Une erreur est survenue lors de la tentative de connexion. Réessayez plus tard.',
            'reload_on_close': False,
        })
    

def logout_simple_sur_home_page(request):
    django_logout(request)
    return redirect("home_app:home-page")

def logout_sur_ERP(request):
    django_logout(request)
    return redirect("auth_app:interface-login-page")  
    



class ChangePasswordView(LoginRequiredMixin, FormView):
    form_class = ChangePasswordForm

    def get_template_names(self):
        user = self.request.user
        role = getattr(user, "role", None)

        if user.is_superuser or role == "directeur":
            return ["directeur_templates/directeur.html"]
        elif role == "commercial":
            return ["commercial_templates/commercial.html"]
        return ["clients_templates/client.html"]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        new_password = form.cleaned_data.get("new_password")

        # 💾 1. Modification atomique du mot de passe
        with transaction.atomic():
            user.set_password(new_password)
            user.save()

            # Maintient la session active malgré la modification du mot de passe
            update_session_auth_hash(self.request, user)

            # ✉️ 2. Préparation et envoi asynchrone de l'email via Celery
            if user.email:
                html_message = render_to_string(
                    "emails/auth/changement_mdp.html",
                    {
                        "user": user,
                        "date": timezone.now(),
                    },
                )
                plain_message = strip_tags(html_message)

                transaction.on_commit(
                    lambda: send_email_task.delay(
                        subject="🔐 Votre mot de passe a été modifié - KOZ Services",
                        plain_message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        html_message=html_message,
                    )
                )

        # 🔄 3. Réponse HTMX
        response = render(
            self.request,
            "partials/auth/_password_change_result.html",
            {
                "success": True,
                "title": "✅ Réussi",
                "message": "🔐 Votre mot de passe a été modifié avec succès",
                "reload_on_close": True,
            },
        )
        response["HX-Trigger"] = "closeChangePassModal"
        return response

    def form_invalid(self, form):
        return render(
            self.request,
            "partials/auth/_password_change_form_errors.html",
            {"change_pass_form": form},
        )
    
    
        
        
         
    
    