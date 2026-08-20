from django.urls import path
from . import views

app_name = "vehicul_app"

urlpatterns = [
    
     # ✅ Nouvelle URL SEO-friendly
    
    
    path("nouveau/vehicule/", views.ERP_CreateVehiculView.as_view(), name="ajout-vehicul"),
    path("nouvelle/marque/", views.ERP_CreateMarqueView.as_view(), name="ajout-marque"),
    #Vehicul URLs
    path("list/vehicule/", views.ERP_VehiculListView.as_view(), name="list-vehicul"),
    path("detail/vehicule/<int:pk>/", views.ERP_VehiculDetailView.as_view(), name="detail-vehicul"),
    path("update/vehicule/<int:pk>/", views.ERP_VehiculUpdateView.as_view(), name="update-vehicul"),
    path("delete/vehicule/<int:pk>/", views.ERP_VehiculDeleteView.as_view(), name="delete-vehicul"),
    
    #Marque URLs
    path("list/marque/", views.ERP_MarqueListView.as_view(), name="list-marque"),
    path("detail/marque/<int:pk>/", views.ERP_MarqueDetailView.as_view(), name="detail-marque"),
    path("update/marque/<int:pk>/", views.ERP_MarqueUpdateView.as_view(), name="update-marque"),
    path("delete/marque/<int:pk>/", views.ERP_MarqueDeleteView.as_view(), name="delete-marque"),
    
     
    path('images/<int:pk>/', views.VehiculeImageListView.as_view(), name='vehicul-images-list'),
    path("suprrimer/image/<int:pk>/", views.VehiculeImageDeleteView.as_view(), name="delete-vehicul-image"),
    path("ajout/images/<int:pk>/", views.ajouter_image, name="ajouter-image"),
    
    # ✅ API publique
    path('api/vehicules/', views.APIVehiculListView.as_view(), name='api-vehicul-list'),
    path('api/vehicules/<int:pk>/',views.APIVehiculDetailView.as_view(), name='api-vehicul-detail'),
    
    # ✅ Types de véhicules
    path('types/', views.ERP_TypeVehiculeListView.as_view(), name='type-vehicul-list'),
    path('type/creer/', views.ERP_CreateTypeVehiculeView.as_view(), name='type-vehicul-create'),
    path('type/<int:pk>/', views.ERP_TypeVehiculeDetailView.as_view(), name='type-vehicule-detail'),
    path('type/<int:pk>/update/', views.ERP_TypeVehiculeUpdateView.as_view(), name='type-vehicul-update'),
    path('type/<int:pk>/delete/', views.ERP_TypeVehiculeDeleteView.as_view(), name='type-vehicul-delete'),
    
    # ✅ SITE PUBLIC : Vues publiques sans authentification
    path('site/vehicules/', views.SITE_VehiculListView.as_view(), name='site-vehicul-list'),
    path('vehicule/<slug:slug>/', views.SITE_VehiculDetailView.as_view(), name='site-vehicul-detail-slug'),
    path('site/vehicule/<int:pk>/', views.SITE_VehiculDetailView.as_view(), name='site-vehicul-detail'),
    path('site/vehicules/type/<int:type_pk>/', views.SITE_VehiculByTypeListView.as_view(), name='site-vehicul-type-list'),
    path('site/marques/', views.SITE_MarqueListeView.as_view(), name='site-marque-list'),
    path('site/marque/<int:pk>/', views.SITE_MarqueDetailView.as_view(), name='site-marque-detail'),
    path('vehicul/images/<int:vehicul_id>/', views.vehicul_image_partials, name="vehicul-image-partial"),
    path('vehicul/contacter/<int:vehicul_id>/', views.contacter_vehicule, name="contacter-vehicule"),
    path('vehicul/favoris/<int:vehicul_id>/', views.toggle_favori, name="ajout-favoris")
    ]