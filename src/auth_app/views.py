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


def site_user_register(request):
    time.sleep(3)
    """Crée un compte utilisateur depuis le site et affiche le résultat dans un partial."""
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

    context = {
        'success': False,
        'title': 'Inscription échouée',
        'message': 'Une erreur est survenue lors de l inscription.',
        'reload_on_close': False,
    }

    if not email or not nom_complet or not telephone or not password or not password2 or not pays or not ville:
        context['message'] = 'Tous les champs obligatoires doivent être remplis.'
        response = render(request, 'partials/auth/register_result.html', context)
        response['HX-Trigger'] = "closeRegisterModal"
        return response

    if password != password2:
        context['message'] = 'Les mots de passe ne correspondent pas.'
        response = render(request, 'partials/auth/register_result.html', context)
        response['HX-Trigger'] = "closeRegisterModal"
        return response

    if len(password) < 6:
        context['message'] = 'Le mot de passe doit contenir au moins 6 caractères.'
        response = render(request, 'partials/auth/register_result.html', context)
        response['HX-Trigger'] = "closeRegisterModal"
        return response

    if kozUser.objects.filter(email=email).exists():
        context['message'] = 'Un compte existe déjà avec cette adresse e-mail.'
        response = render(request, 'partials/auth/register_result.html', context)
        response['HX-Trigger'] = "closeRegisterModal"
        return response

    try:
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

        context['success'] = True
        context['title'] = 'Inscription réussie'
        context['message'] = 'Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.'
        context['reload_on_close'] = True
    except Exception as e:
        logger.error(f"Erreur création compte site: {e}")
        context['message'] = 'Impossible de créer votre compte pour le moment. Veuillez réessayer plus tard.'

    response = render(request, 'partials/auth/register_result.html', context)
    response["HX-Trigger"] = "closeRegisterModal"
    return response


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
        kwargs =  super().get_form_kwargs()
        kwargs["created_by"] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        if self.request.user.role == 'commercial':
            form.instance.role = 'client'
            form.instance.is_active = True
            form.instance.assigned_commercial = self.request.user
        
        user = form.save()   # ✅ toujours appelé, peu importe qui crée
        
        response = render(self.request, 'partials/auth/register_result.html', {
            'success': True,
            'title': f"Utilisateur {user.nom_complet} créé !",
            'message': "📧 Les identifiants temporaires ont été envoyés par email.",
            'reload_on_close': True,
        })
        response["HX-Trigger"] = "closeRegisterModal"
        return response
    
    def form_invalid(self, form):
        return render(self.request, 'partials/auth/_user_register_form_errors.html', {"user_register_form":form})


def login_simple(request):
    if request.method != 'POST':
        return redirect("home_app:home-page")

    try:
        email = (request.POST.get('email') or '').strip()
        password = request.POST.get('password') or ''

        if not email or not password:
            response = render(request, "partials/auth/login_result.html", {
                'success': False,
                'title': 'Connexion impossible',
                'message': 'Veuillez renseigner votre email et votre mot de passe.',
                'reload_on_close': False,
            })
            response["HX-Trigger"] = "closeLoginModal"
            return response

        user = authenticate(request, email=email, password=password)

        if user is None:
            response = render(request, "partials/auth/login_result.html", {
                'success': False,
                'title': 'Email ou mot de passe incorrect',
                'message': 'Vérifiez vos identifiants et réessayez.',
                'reload_on_close': False,
            })
            response["HX-Trigger"] = "closeLoginModal"
            return response

        # Tout est ok -> connexion
        django_login(request, user)

        response = render(request, "partials/auth/login_result.html", {
            'success': True,
            'title': f'Bienvenue, {user.nom_complet}',
            'message': 'Connexion réussie',
            'reload_on_close': True,
        })
        response["HX-Trigger"] = "closeLoginModal"
        return response

    except Exception as e:
        logger.exception(f"Erreur lors de login_simple: {e}")
        response = render(request, "partials/auth/login_result.html", {
            'success': False,
            'title': 'Erreur serveur',
            'message': 'Une erreur est survenue lors de la tentative de connexion. Réessayez plus tard.',
            'reload_on_close': False,
        })
        response["HX-Trigger"] = "closeLoginModal"
        return response
    

def logout_simple_sur_home_page(request):
    django_logout(request)
    return redirect("home_app:home-page")

def logout_sur_ERP(request):
    django_logout(request)
    return redirect("auth_app:interface-login-page")  
    
class ChangePasswordView(LoginRequiredMixin, FormView):
    form_class = ChangePasswordForm
    time.sleep(1.5)
    def get_template_names(self):
        if self.request.user.is_superuser or self.request.user.role == "directeur":
            return ["directeur_templates/directeur.html"]
        elif self.request.user.role == "commercial":
            return ["commercial_templates/commercial.html"]
        else:
            return ["clients_templates/client.html"]
           

    def get_form_kwargs(self):
        kwargs =  super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs
    
    


    def form_valid(self, form):
        new_password = form.cleaned_data.get("new_password")
        
        user = self.request.user
        user.set_password(new_password)
        user.save()
        
        #Reconnecte le User
        
        update_session_auth_hash(self.request, user)
        
        # ✉️ Envoi d'email de confirmation
         # ✉️ Email HTML
        html_message = render_to_string('emails/auth/changement_mdp.html', {
            'user': user,
            'date': timezone.now(),
        })
        plain_message = strip_tags(html_message)

        try:
            send_mail(
                subject="🔐 Votre mot de passe a été modifié - KOZ Services",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Erreur envoi email: {e}")
    
        
        
        
        response = render(self.request, "partials/auth/_password_change_result.html", {
            "success": True,
            "title" : "✅ Réussi",
            "message":"🔐 Votre mot de passe a été modifié avec succès",
            "reload_on_close": True
        })
        response["HX-Trigger"] = "closeChangePassModal"
        return response
        
    def form_invalid(self, form):
       return render(self.request, 'partials/auth/_password_change_form_errors.html', {"change_pass_form":form})
    
    
        
        
         
    
    