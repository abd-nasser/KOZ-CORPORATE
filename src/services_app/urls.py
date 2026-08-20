from django.urls import path
from .views import (
    TypesServicesListView, TypesServicesCreateView,
    ERP_ServicesListView, ERP_ServicesCreateView, ERP_ServiceDetailView, SITE_ServiceAvisCreateView,
    ERP_ServiceAvisApprobationView, SITE_ServiceDetailView,SITE_ServicesListView, 
    ERP_ServiceDeleteView, 
    ERP_ServiceImagesCreateView, 
    ERP_ServiceUpdateView, contacter_service
    )


app_name = 'services_app'

urlpatterns = [
    # Types
    path('types/', TypesServicesListView.as_view(), name='types-services-list'),
    path('types/creer/', TypesServicesCreateView.as_view(), name='types-services-create'),
    
    # Services_ERP
    path('creer/', ERP_ServicesCreateView.as_view(), name='services-create'),
    path('list/', ERP_ServicesListView.as_view(), name='services-list'),
    path('detail/<int:pk>/service/admin',ERP_ServiceDetailView.as_view(), name='service-detail'),
    path('modifier/<int:pk>/service/admin', ERP_ServiceUpdateView.as_view(), name="service-update"),
    path("supprimer/<int:pk>/service/admin", ERP_ServiceDeleteView.as_view(), name="service-delete"),
    path("approuver/<int:pk>/avis", ERP_ServiceAvisApprobationView.as_view(), name="approuver-avis"),
    path("ajouter/image/", ERP_ServiceImagesCreateView.as_view(), name="ajouter-service-image"),
        
    # Services_SITE
    path('detail/<int:pk>/service/public',SITE_ServiceDetailView.as_view(), name="service-detail-public"),
    path('contacter/<int:service_id>/service/public', contacter_service, name="contacter-service"),
    path('list/', SITE_ServicesListView.as_view(), name='services-list-public'),

    
    # Avis
    path("donner/<int:service_pk>/avis", SITE_ServiceAvisCreateView.as_view(), name="service-avis-create"),
   
]