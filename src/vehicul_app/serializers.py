# vehicul_app/serializers.py

from rest_framework import serializers
from .models import Vehicul, Marque, VehiculeImage


class MarqueSerializer(serializers.ModelSerializer):
    """Serializer pour les marques"""
    class Meta:
        model = Marque
        fields = ['id', 'nom', 'logo']


class VehiculeImageSerializer(serializers.ModelSerializer):
    """Serializer pour les images d'un véhicule"""
    class Meta:
        model = VehiculeImage
        fields = ['id', 'image', 'alt_text', 'ordre', 'est_principale']


class VehiculSerializer(serializers.ModelSerializer):
    """Serializer principal pour les véhicules"""
    
    # ✅ Remplacer l'ID de la marque par un objet complet
    marque = MarqueSerializer(read_only=True)
    
    # ✅ Ajouter toutes les images du véhicule
    images = VehiculeImageSerializer(many=True, read_only=True)
    
    # ✅ Ajouter l'image principale (si elle existe)
    image_principale_url = serializers.SerializerMethodField()
    
    # ✅ Ajouter l'URL complète des images
    images_urls = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehicul
        fields = [
            'id',
            'marque',
            'modele',
            'annee',
            'stock',
            'prix',
            'kilometrage',
            'carburant',
            'disponible',
            'description',
            'date_ajout',
            'image_principale',
            'image_principale_url',      # ✅ URL complète
            'images',                     # ✅ Toutes les images
            'images_urls',               # ✅ Liste d'URLs
        ]
    
    def get_image_principale_url(self, obj):
        """Retourne l'URL complète de l'image principale"""
        request = self.context.get('request')
        if obj.image_principale and hasattr(obj.image_principale, 'url'):
            if request:
                return request.build_absolute_uri(obj.image_principale.url)
            return obj.image_principale.url
        return None
    
    def get_images_urls(self, obj):
        """Retourne la liste des URLs de toutes les images"""
        request = self.context.get('request')
        urls = []
        for image in obj.images.all().order_by('ordre'):
            if request:
                urls.append(request.build_absolute_uri(image.image.url))
            else:
                urls.append(image.image.url)
        return urls