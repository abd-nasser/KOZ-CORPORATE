from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

app_name = 'paiement_app'

urlpatterns = [
    path('commande/<int:commande_id>/', views.page_paiement, name='page-paiement'),
    path('commande/<int:commande_id>/initier/', views.initier_paiement, name='initier-paiement'),
    path('confirmation/', views.confirmation_paiement, name='confirmation'),
    path('callback/', csrf_exempt(views.callback_ligdicash), name='callback-ligdicash'),
]