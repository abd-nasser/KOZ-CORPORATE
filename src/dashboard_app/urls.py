from django.urls import path
from . import views
app_name = 'dashboard_app'
urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard-view'),
    path('liste/<str:model_name>/<str:filter_nom>/<str:filter_valeur>/', views.ListeFiltreeView.as_view(), name='liste-filtree'),
]