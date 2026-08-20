from django.urls import path
from . import views

app_name = "commercial_app"

urlpatterns = [
    path("dashboard/", views.CommercialDashboardView.as_view(), name="commercial-view"),
    path("client/list/", views.CommercialClientListFilter.as_view(), name="client-list-filter"),
    path("générer/<int:demande_id>/offre/", views.creer_offre, name="creer-offre"),
    path("offres/", views.OffreView.as_view(), name="offre-list"),
    path("générer/<int:pk>/simple/offre/", views.OffreSimpleCreateView.as_view(), name="creer-offre-simple"),
    path("generer/<int:pk>/offre/financement",views.OffreDeFinancementView.as_view(), name="creer-offre-financement"),
    path("offre/<int:pk>/", views.OffreDetailView.as_view(), name="offre-detail"),  
    path('offre/<int:pk>/modifier/', views.OffreUpdateView.as_view(), name="update-offre"),
    path("offre/simple/<int:pk>/modifier/", views.OffreSimpleUpdate.as_view(), name="update-offre-simple"),
    path('offre/<int:pk>/supprimer/',views.OffreDeleteView.as_view(), name='offre-delete'),
    path("offre/<int:offre_id>/accepter/", views.accepter_offre, name="accepter-offre"),
    path("offre/<int:offre_id>/refuser/", views.refuser_offre, name="refuser-offre"),
    path('offre/<int:offre_id>/negocier/',views.negocier_offre, name='negocier-offre'),


    
    #######################________Maintenance____________#############################
    path('maintenances/',views.MaintenanceListView.as_view(), name='maintenance-list'),
    path('maintenances/ajouter/',views.MaintenanceCreateView.as_view(), name='maintenance-create'),
    path('maintenances/<int:pk>/',views.MaintenanceDetailView.as_view(), name='maintenance-detail'),
    path('maintenances/<int:pk>/modifier/',views.MaintenanceUpdateView.as_view(), name='maintenance-update'),
    path('maintenances/<int:pk>/supprimer/',views.MaintenanceDeleteView.as_view(), name='maintenance-delete'),
    path('maintenances/<int:maintenance_id>/changer_statut/',views.changer_statut_maintenance, name='changer-statut-maintenance'),
    path('confirmer/maintenance/<int:maintenance_id>/',views.confirmer_maintenance, name='confirmer-maintenance'),
    path('refuser/maintenance/<int:maintenance_id>/',views.refuser_maintenance, name='refuser-maintenance'),
    path("changer/statut/maintenance/<int:maintenance_id>/<str:nouveau_statut>/", views.changer_statut_maintenance, name="changer-statut-maintenance"),
    
    
    
    #######################________Vente____________#############################
    path("creer/ventes/simple", views.venteSimpleCreate.as_view(), name="create-simple-vente"),
    path('ventes/',views.VenteListView.as_view(), name='vente-list'),
    path('ventes/<int:pk>/detail', views.VenteDetailView.as_view(), name="vente-detail"),
    path('ventes/partial/', views.VenteListView.as_view(), name='vente-list-partial'),
    path('vente/<int:vente_id>/changer-statut/',views.changer_statut_vente, name='changer-statut-vente'),
    path('vente/<int:vente_id>/marquer-paye/<int:numero_echeance>/', views.marquer_paye, name='marquer-paye'),
    
    
    ########################________RendezVous____________#############################
     path('rendez-vous/', views.CommercialRendezVousListView.as_view(), name='rendez-vous-list'),
    path('rendez-vous/confirmer/<int:rdv_id>/', views.confirmer_rdv, name='confirmer-rdv'),
    path('rendez-vous/annuler/<int:rdv_id>/', views.annuler_rdv, name='annuler-rdv'),
    path('rendez-vous/terminer/<int:rdv_id>/', views.terminer_rdv, name='terminer-rdv'),
]
