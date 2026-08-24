from django.urls import path
from . import views

app_name = "client_app"

urlpatterns = [
    path("dashboard/", views.ClientDashboardView.as_view(), name="client-view"),
    path("detail/<int:pk>/", views.ClientDetailView.as_view(), name="client-detail"),
    path('clients/rendez-vous/', views.MesRendezVousListView.as_view(), name='mes-rendez-vous'),
    path('client/creer/rendez-vous', views.ClientRdvCreateView.as_view(), name="client-create-rdv")
]
