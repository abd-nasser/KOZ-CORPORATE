from rest_framework import serializers
from .models import Products, CategorieProducts, ProductsImage

class CategorieProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategorieProducts
        fields = ["id", "nom"]  # ← Ajout de l'id


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductsImage
        fields = ["id", "image", "alt_text", "ordre", "est_principale"]  # ← 'image' pas 'images'


class ProductsSerializer(serializers.ModelSerializer):
    categorie = CategorieProductsSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    image_principale_url = serializers.SerializerMethodField()
    images_urls = serializers.SerializerMethodField()
    
    class Meta:
        model = Products
        fields = [
            "id",
            "nom",
            "prix",
            "stock",
            "compatible_avec",
            "categorie",  # ← Ajouter la catégorie (objet complet)
            "image_principale",
            "image_principale_url",
            "images",
            "images_urls",
        ]
    
    def get_image_principale_url(self, obj):
        request = self.context.get('request')
        if obj.image_principale and hasattr(obj.image_principale, "url"):
            if request:
                return request.build_absolute_uri(obj.image_principale.url)
            return obj.image_principale.url
        return None
    
    def get_images_urls(self, obj):
        request = self.context.get("request")
        urls = []
        for image in obj.images.all():
            if request:
                urls.append(request.build_absolute_uri(image.image.url))
            else:
                urls.append(image.image.url)  # ← Correction ici
        return urls