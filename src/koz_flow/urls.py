from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from koz_flow.views import health_check

from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap, VehiculSitemap, ProduitSitemap

urlpatterns = [
    path("", include("home_app.urls")),
    path('api/auth/', include('auth_app.urls')),
    path("directeur/", include("directeur_app.urls")),
    path("commercial/", include("commercial_app.urls")), 
    path('client/', include("client_app.urls")),
    path('chat/', include("chat_app.urls")),
    path('vehicule/', include("vehicul_app.urls")),
    path('products/', include('products_app.urls')),
    path('services/', include("services_app.urls")),
    path("leads/", include("leads_app.urls")),
    path("dashboard/", include("dashboard_app.urls")),
    path('api/order/', include('order_app.urls')),
    path("api/paiement/", include("paiement_app.urls")),
    
    path('health/', health_check, name='health-check'),
    path('koz_adminitration_2k26/', admin.site.urls),
]


sitemaps = {
    'pages': StaticViewSitemap,
    'vehicules': VehiculSitemap,
    'produits': ProduitSitemap,
}

urlpatterns += [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)