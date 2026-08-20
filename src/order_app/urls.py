# order_app/urls.py

from django.urls import path
from . import views 

app_name = "order_app"
urlpatterns = [
    

    path('panier/', views.panier_view, name='panier'),
    path('panier/ajouter/<int:product_id>/', views.ajouter_article, name="ajouter-article"),
    path('panier/modifier/<int:article_id>/', views.modifier_quantite, name='modifier-panier'),
    path('panier/retirer/<int:article_id>/', views.retirer_article, name='retirer-panier'),
    path('panier/vider/', views.vider_panier, name='vider-panier'),
    path('valider-commande/', views.valider_commande, name='valider-commande'),
    path('annuler-commande/<int:commande_id>/', views.annuler_commande, name='annuler-commande'),
    path('detail/commande/<int:pk>/', views.CommandDetailView.as_view(), name="detail-commande")
]