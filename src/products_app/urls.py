from django.urls import path
from .views import (
    CategorieProductsListView, CategorieProductsCreateView, CategorieProductsUpdateView, CategorieProductsDeleteView,
    MarqueProduitListView, MarqueProduitCreateView, MarqueProduitUpdateView, MarqueProduitDeleteView,
    UniteProduitListView, UniteProduitCreateView, UniteProduitUpdateView, UniteProduitDeleteView,
    ProductsListView, ProductsCreateView, ProductsDetailView, ProductsUpdateView, ProductsDeleteView,
    ApiProductListView, ApiProductsdetail, ProductsImageListView, ProductImageDeleteView,
    filter_products_by_category, ajouter_image, toggle_product_favoris
)
# products_app/urls.py

app_name = 'products_app'

urlpatterns = [
    # Catégories
    path('categories/', CategorieProductsListView.as_view(), name='categorie-products-list'),
    path('categories/ajouter/', CategorieProductsCreateView.as_view(), name='categorie-products-create'),
    path('categories/<int:pk>/modifier/', CategorieProductsUpdateView.as_view(), name='categorie-products-update'),
    path('categories/<int:pk>/supprimer/', CategorieProductsDeleteView.as_view(), name='categorie-products-delete'),
    
    # Marques
    path('marques/', MarqueProduitListView.as_view(), name='marque-produit-list'),
    path('marques/ajouter/', MarqueProduitCreateView.as_view(), name='marque-produit-create'),
    path('marques/<int:pk>/modifier/', MarqueProduitUpdateView.as_view(), name='marque-produit-update'),
    path('marques/<int:pk>/supprimer/', MarqueProduitDeleteView.as_view(), name='marque-produit-delete'),

    # Unités
    path('unites/', UniteProduitListView.as_view(), name='unite-produit-list'),
    path('unites/ajouter/', UniteProduitCreateView.as_view(), name='unite-produit-create'),
    path('unites/<int:pk>/modifier/', UniteProduitUpdateView.as_view(), name='unite-produit-update'),
    path('unites/<int:pk>/supprimer/', UniteProduitDeleteView.as_view(), name='unite-produit-delete'),
    
    # Produits
    path('', ProductsListView.as_view(), name='products-list'),
    path('ajouter/', ProductsCreateView.as_view(), name='products-create'),
     # ✅ URL SEO-friendly avec slug
    path('produit/<slug:slug>/', ProductsDetailView.as_view(), name='detail-produit-slug'),
    path('<int:pk>/', ProductsDetailView.as_view(), name='products-detail'),
    path('<int:pk>/modifier/', ProductsUpdateView.as_view(), name='products-update'),
    path('<int:pk>/supprimer/', ProductsDeleteView.as_view(), name='products-delete'),
    path('products/images/<int:pk>/', ProductsImageListView.as_view(), name='product-images-list'),
    path('supprimer/image/<int:pk>/', ProductImageDeleteView.as_view(), name='delete-product-image'),
    
    # Filtre
    path('categorie/<int:category_id>/', filter_products_by_category, name='products-by-category'),
    path('ajouter/favoris/<int:product_id>/',toggle_product_favoris, name="products-favoris"),
    # ajout_images
    path('ajouter/image/<int:pk>/', ajouter_image, name='ajouter-image'),
    # API
    path('api/products/list/', ApiProductListView.as_view(), name='api-products-list'),
    path('api/product/<int:pk>/', ApiProductsdetail.as_view(), name='api-product-detail')
]