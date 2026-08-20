from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from chat_app import views
from .views import (ApiRegisterView, LoginView, 
                    MeView, LogoutView, site_user_register,
                    UserRegisterView, ChangePasswordView, login_page, login_simple, logout_simple_sur_home_page, logout_sur_ERP)

app_name = "auth_app"

urlpatterns = [
    
    #path("", views.home_page_view, name="home-page")
    path("interface/connection", login_page, name="interface-login-page"),
    
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
    path('logout/sur/ERP', logout_sur_ERP, name="logout-sur-erp" )
]
