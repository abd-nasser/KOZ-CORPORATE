# koz_flow/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from vehicul_app.models import Vehicul
from products_app.models import Products  # Vérifie que le nom du modèle est correct


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return [
            'home_app:home-page',
            'vehicul_app:list-vehicul',
            'leads_app:demande-financement',
            'services_app:services-list-public',
        ]

    def location(self, item):
        return reverse(item)


class VehiculSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Vehicul.objects.filter(disponible=True)

    def lastmod(self, obj):
        return obj.date_ajout


class ProduitSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Products.objects.all()

    def lastmod(self, obj):
        return obj.date_ajout if hasattr(obj, 'date_ajout') else None

    # ✅ Supprime la méthode location() – Django s'en occupe via get_absolute_url()
    # Ou alors, assure-toi que ton modèle a une méthode get_absolute_url()