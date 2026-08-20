from django.urls import path, include
from . import views

app_name = "home_app"

urlpatterns = [
    path("", views.home_page_view, name="home-page"),
    
     #Actions for TemoignageTextuel
    path("approuver/temoignage/<int:temoignage_id>/", views.approuver_temoignage, name="approuver-temoignage"),
    path("rejeter/temoignage/<int:temoignage_id>/", views.rejeter_temoignage, name="rejeter-temoignage"),
    path("temoignages/delete/<int:pk>/", views.delete_textuel_temoignage, name="delete-temoignage"),
    path("vehicules-vedette/partial/", views.vehicules_partial, name="vehicules-vedette-partial"),
    
    path("temoignages/ajout/", views.TextuelTemoignageCreateView.as_view(), name="ajout-textuel-temoignage"),
    path("temoignages/", views.TemoignageTextuelListView.as_view(), name="temoignages-textuel-list"),
    
    #Actions for AvisReseau
    path("activer-avis-reseau/<int:avis_id>/", views.activer_avis_reseau, name="activer-avis-reseau"),
    path("desactiver-avis-reseau/<int:avis_id>/", views.desactiver_avis_reseau, name="desactiver-avis-reseau"),
    path("avis-reseau/ajout/", views.CreateAvisReseauView.as_view(), name="ajout-avis-reseau"),
    path("avis-reseau/list/", views.ListeAvisReseauView.as_view(), name="avis-reseau-list"),
    
    #Actions for VideoTemoignage
    path("video-temoignages/", views.VideoTemoignageListView.as_view(), name="video-temoignages-list"),
    path("video-temoignages/ajout/", views.VideoTemoingnageCreateView.as_view(), name="ajout-video-temoignage"),
   
    
    #Actions for Actualite
    path("actualites/", views.ActualiteListView.as_view(), name="actualites-list"),
    path("actualites/ajouter/", views.ActualiteCreateView.as_view(), name="actualites-create"),
    path("actualites/<int:pk>/", views.ActualiteDetailView.as_view(), name="actualites-detail"),
    path("actualites/<int:pk>/modifier/", views.ActualiteUpdateView.as_view(), name="actualites-update"),
    path("actualites/<int:pk>/supprimer/", views.delete_actualite, name="actualites-delete"),
    
    #Actions for contact form
    path("contact/", views.contact_form, name="contact-form"),
    path("rdv/", views.prise_rdv, name="prise-rdv"),

]
