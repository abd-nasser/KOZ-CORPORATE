from django.urls import path
from . import views

app_name = "directeur_app"

urlpatterns = [
    path('dashboard/',views.DirecteurDashboardView.as_view(), name="directeur-view"),
    path('rendez-vous/', views.DirecteurRendezVousListView.as_view(), name='rendez-vous-list'),
]
