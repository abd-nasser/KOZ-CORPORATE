from django.contrib import admin

from .models import Products, CategorieProducts, MarqueProduit, UniteProduit, ProductsImage


@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ['nom', 'categorie', 'marque', 'prix', 'stock']
 

    
    
@admin.register(CategorieProducts)
class CategorieProductsAdmin(admin.ModelAdmin):
    list_display = ['nom', 'est_active', 'ordre']

    

@admin.register(MarqueProduit)
class MarqueProduitAdmin(admin.ModelAdmin):
    list_display = ['nom', 'est_active']

   