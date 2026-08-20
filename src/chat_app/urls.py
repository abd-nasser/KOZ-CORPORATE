from django.urls import path
from . import views

app_name = "chat_app"

urlpatterns = [
    # Vue pour afficher la discussion
    path('', views.chat_view, name="chat-view"),                        # Client
    path('<int:client_id>/', views.chat_view, name="chat-view"),        # Commercial

    # Vue pour envoyer un message (POST)
    path('envoyer/', views.envoyer_message, name="client_envoyer_message"),                      # Client
    path('envoyer/<int:client_id>/', views.envoyer_message, name="commercial_envoyer_message"),      # Commercial
]
