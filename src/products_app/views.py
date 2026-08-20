# products_app/views.py
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import CategorieProducts, MarqueProduit, UniteProduit, Products, ProductsImage
from .forms import CategorieProductsForm, MarqueProduitForm, UniteProduitForm, ProductsForm, ProductImageForm
from chat_app.models import Message
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings

import logging

logger = logging.getLogger(__name__)
# ============================================================
# CRUD Catégories
# ============================================================

class CategorieProductsListView(ListView):
    model = CategorieProducts
    template_name = 'products_templates/categorie_products_list.html'
    context_object_name = 'categories'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'create_categorie_form' not in context:
            context['create_categorie_form'] = CategorieProductsForm()
        return context

class CategorieProductsCreateView(CreateView):
    model = CategorieProducts
    form_class = CategorieProductsForm
    template_name = 'products_templates/categorie_products_list.html'
    success_url = reverse_lazy('products_app:categorie-products-list')

class CategorieProductsUpdateView(UpdateView):
    model = CategorieProducts
    form_class = CategorieProductsForm
    template_name = 'products_templates/categorie_products_form.html'
    success_url = reverse_lazy('products_app:categorie-products-list')

class CategorieProductsDeleteView(DeleteView):
    model = CategorieProducts
    template_name = 'products_templates/categorie_products_confirm_delete.html'
    success_url = reverse_lazy('products_app:categorie-products-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Vous pouvez ajouter des messages de succès ici si vous utilisez le framework de messages de Django
        messages.success(self.request, "Nouvelle categorie ajoutée avec succès !")
        return response
    
    def form_invalid(self, form):
        listView = ProductsListView()
        listView.request = self.request  # Simule une requête pour pouvoir accéder aux catégories
        listView.object_list = listView.get_queryset() 
        listView.kwargs = self.kwargs
        context = listView.get_context_data()
        context['create_categorie_form'] = form # Formulaire avec les erreurs
        context["open_create_categorie_form"] = True # Indicateur pour ouvrir le modal
        
        messages.error(self.request, "Erreur lors de la création du catégories. Veuillez vérifier les informations saisies.")
        return self.render_to_response(context)


# ============================================================
# CRUD Produits
# ============================================================

from django.views.generic import ListView
from django.db.models import Q
from .models import Products, CategorieProducts, MarqueProduit, UniteProduit
from .forms import ProductsForm

class ProductsListView(ListView):
    model = Products
    template_name = 'products_templates/SITE/SITE_products_list.html'
    context_object_name = 'products'
    paginate_by = 12


    def get_queryset(self):
        queryset = Products.objects.filter(est_disponible=True).select_related('categorie', 'marque', 'unite')
        
        # ✅ Recherche
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(nom__icontains=q) |
                Q(description__icontains=q) |
                Q(description_courte__icontains=q) |
                Q(marque__nom__icontains=q) |
                Q(categorie__nom__icontains=q)
            )
        
        # ✅ Filtre par catégorie
        categorie = self.request.GET.get('categorie')
        if categorie:
            queryset = queryset.filter(categorie_id=categorie)
        
        # ✅ Filtre par marque
        marque = self.request.GET.get('marque')
        if marque:
            queryset = queryset.filter(marque_id=marque)
        
        # ✅ Filtre par prix min
        prix_min = self.request.GET.get('prix_min')
        if prix_min:
            try:
                queryset = queryset.filter(prix__gte=prix_min)
            except ValueError:
                pass
        
        # ✅ Filtre par prix max
        prix_max = self.request.GET.get('prix_max')
        if prix_max:
            try:
                queryset = queryset.filter(prix__lte=prix_max)
            except ValueError:
                pass
        
        # ✅ Filtre par stock
        stock = self.request.GET.get('stock')
        if stock == 'en_stock':
            queryset = queryset.filter(stock__gt=0)
        elif stock == 'rupture':
            queryset = queryset.filter(stock__lte=0)
        
        # ✅ Filtre par promo
        promo = self.request.GET.get('promo')
        if promo == 'true':
            queryset = queryset.filter(prix_promo__isnull=False)
        
        # ✅ Tri
        sort = self.request.GET.get('sort')
        if sort == 'prix_asc':
            queryset = queryset.order_by('prix')
        elif sort == 'prix_desc':
            queryset = queryset.order_by('-prix')
        elif sort == 'nom_asc':
            queryset = queryset.order_by('nom')
        else:
            queryset = queryset.order_by('-date_ajout')  # Par défaut : plus récent
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CategorieProducts.objects.filter(est_active=True)
        context['marques'] = MarqueProduit.objects.filter(est_active=True)
        
        # ✅ Conserver les filtres dans l'URL pour la pagination
        context['filters'] = self.request.GET.copy()
        
        return context
class ProductsCreateView(CreateView):
    model = Products
    form_class = ProductsForm
    template_name = 'products_templates/products_list.html'
    success_url = reverse_lazy('products_app:products-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Vous pouvez ajouter des messages de succès ici si vous utilisez le framework de messages de Django
        messages.success(self.request, "Produit créé avec succès !")
        return response
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        listView = ProductsListView()
        listView.request = self.request  # Simule une requête pour pouvoir accéder aux catégories
        listView.object_list = listView.get_queryset() 
        listView.kwargs = self.kwargs
        context = listView.get_context_data()
        context['create_product_form'] = form # Formulaire avec les erreurs
        context["open_create_product_modal"] = True # Indicateur pour ouvrir le modal
        
        messages.error(self.request, "Erreur lors de la création du produit. Veuillez vérifier les informations saisies.")
        return self.render_to_response(context)

class ProductsDetailView(DetailView):  # ← DetailView, 
    model = Products
    template_name = 'products_templates/SITE/SITE_product_detail.html'
    context_object_name = 'produit'
    
    def get_object(self):
        if 'pk' in self.kwargs:
            return get_object_or_404(Products, pk=self.kwargs['pk'])
        elif 'slug' in self.kwargs:
            return get_object_or_404(Products, slug=self.kwargs['slug'])
        raise Http404("Produit non trouvé")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CategorieProducts.objects.all()
        context['update_product_form'] = ProductsForm(instance=self.object)
        
         # ✅ Images du véhicule
        images = self.object.images.all().order_by('ordre', 'date_ajout')
        context["images"] = images
        
        # ✅ Image principale (fallback si pas trouvée)
        image_principal = images.filter(est_principale=True).first()
        if not image_principal and images.exists():
            image_principal = images.first()
        context["image_principal"] = image_principal
        return context

class ProductsImageListView(LoginRequiredMixin, ListView):
    model= ProductsImage
    template_name = 'products_templates/product_images_list.html'
    context_object_name = "images"
    paginate_by = 8
    
    def get_queryset(self):
        self.product = get_object_or_404(Products, pk=self.kwargs["pk"])
        return self.product.images.all().order_by('ordre')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product"] = self.product
        if "product_image_form" not in context:
            context["product_image_form"] = ProductImageForm()
        return context

def toggle_product_favoris(request, product_id):
    if request.user.is_anonymous or request.user.role != 'client':
        response = render(request, "partials/products/_products_favori_result.html", {
                    "success": False,
                    "title": "❌ Action non autorisée",
                    "message": "Seuls les clients ou abonnée peuvent ajouter des favoris.",
                })
        return response
    
    product = get_object_or_404(Products, id=product_id)
    
    if product.favoris_de.filter(id=request.user.id).exists():
        product.favoris_de.remove(request.user)
        ajoute = False
    else:
        product.favoris_de.add(request.user)
        ajoute = True
        
        Message.objects.create(
            client=request.user,
            commercial=None,
            contenu=(
                f"Vous avez ajouté {product.marque.nom} {product.nom} à vos favoris. "
                f"N'hésitez pas à échanger avec un conseiller sur les different produits"
                            ),
            est_client=False,
            lu=False,
            origine_automatique=True  
            ),
        if request.user.email:
            try:
                lien_chat = request.build_absolute_uri(reverse('chat_app:chat-view'))
                html_message = render_to_string('emails/products/products_notif_favori.html', {
                        'client': request.user,
                        'produit': f"{product.marque.nom} {product.nom}",
                        'lien_chat': lien_chat,
                    })
                send_mail(
                            subject=f"💬 Nouveau message concernant {product.marque.nom} {product.nom}",
                            message=strip_tags(html_message),
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[request.user.email],
                            html_message=html_message,
                            fail_silently=False,
                        )
            except Exception as e:
                logger.error(f"Erreur email notif favori pour {request.user.email}: {e}")
    return render(request, "partials/products/_product_favori_button.html", {"produit": product})
            
        
# ============================================================================================
# ✅ AJOUT : Ajouter une Image(FBV)
# ============================================================================================
@login_required
@require_POST
def ajouter_image(request, pk):
    product = get_object_or_404(Products, pk=pk)
    
    #✅ Vérification des permissions
    if not (request.user.is_superuser or request.user.role =="directeur"):
        messages.error(request, "Vous n'avez pas la permission d'ajouter des images.")
        return redirect('products_app:products-detail', product.pk)
    
    #✅ Traitement de formulaire
    form = ProductImageForm(request.POST, request.FILES)
    if form.is_valid():
        image = form.save(commit=False)
        image.product = product
        image.save()
        
        #✅ SI l'image est Principale, désactiver les autres
        if image.est_principale:
            ProductsImage.objects.filter(
                product=product
            ).exclude(pk=image.pk).update(est_principale=False)
        messages.success(request, "✅ Image ajoutée avec succès")
    else:
        messages.error(request, f"❌ Erreur dans le formulaire:{form.errors}")
    
    #✅ Redirection vers la page d'images
    return redirect("products_app:product-images-list", product.pk)
        
                
#======================================================================================================
#✅ SUPPRESSION : Supprimer une Image 
#======================================================================================================
class ProductImageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ProductsImage
    template_name = "products_templates/product_image_delete.html"
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    def get_success_url(self):
        return reverse_lazy('products_app:products-detail', kwargs={'pk': self.object.pk})
    def delete(self, request, *args, **kwargs):
        response =  super().delete(request, *args, **kwargs)
        messages.success(request, "Image supprimée avec succès")
        return response 


class ProductsUpdateView(UpdateView):
    model = Products
    form_class = ProductsForm
    template_name = 'products_templates/products_detail.html'

    def get_success_url(self):
        return reverse_lazy('products_app:products-detail', kwargs={'pk': self.object.pk})

class ProductsDeleteView(DeleteView):
    model = Products
    template_name = 'products_templates/confirm_products_delete.html'
    success_url = reverse_lazy('products_app:products-list')


# ============================================================
# Filtre par catégorie (FBV ou CBV au choix)
# ============================================================

# Option 1 : FBV (simple)
def filter_products_by_category(request, category_id):
    category = get_object_or_404(CategorieProducts, id=category_id)
    products = Products.objects.filter(categorie=category)
    return render(request, 'products_templates/products-list.html', {
        'products': products,
        'categories': CategorieProducts.objects.all()
    })

# Option 2 : CBV (plus propre)
class ProductsByCategoryListView(ListView):
    model = Products
    template_name = 'products_templates/products-list.html'
    context_object_name = 'products'

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        return Products.objects.filter(categorie_id=category_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CategorieProducts.objects.all()
        return context


# ============================================================
# CRUD Marques de produits
# ============================================================

class MarqueProduitListView(ListView):
    model = MarqueProduit
    template_name = 'products_templates/marque_produit_list.html'
    context_object_name = 'marques'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'create_marque_form' not in context:
            context['create_product_marque_form'] = MarqueProduitForm()
        return context


class MarqueProduitCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == 'directeur'

    def get_success_url(self):
        return reverse_lazy("directeur_app:directeur-view")
    
    model = MarqueProduit
    form_class = MarqueProduitForm
    template_name = 'products_templates/marque_produit_form.html'


    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Marque ajoutée avec succès.')
        return response


class MarqueProduitUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == 'directeur'

    model = MarqueProduit
    form_class = MarqueProduitForm
    template_name = 'products_templates/marque_produit_form.html'
    success_url = reverse_lazy('products_app:marque-produit-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Marque mise à jour avec succès.')
        return response


class MarqueProduitDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == 'directeur'

    model = MarqueProduit
    template_name = 'products_templates/marque_produit_confirm_delete.html'
    success_url = reverse_lazy('products_app:marque-produit-list')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Marque supprimée avec succès.')
        return response


# ============================================================
# CRUD Unités de produits
# ============================================================

class UniteProduitListView(ListView):
    model = UniteProduit
    template_name = 'products_templates/unite_produit_list.html'
    context_object_name = 'unites'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'create_unite_form' not in context:
            context['create_unite_form'] = UniteProduitForm()
        return context


class UniteProduitCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == 'directeur'

    model = UniteProduit
    form_class = UniteProduitForm
    template_name = 'directeur_templates/directeur.html'
    success_url = reverse_lazy('products_app:unite-produit-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Unité ajoutée avec succès.')
        return response


class UniteProduitUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == 'directeur'

    model = UniteProduit
    form_class = UniteProduitForm
    template_name = 'products_templates/unite_produit_form.html'
    success_url = reverse_lazy('products_app:unite-produit-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Unité mise à jour avec succès.')
        return response


class UniteProduitDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == 'directeur'

    model = UniteProduit
    template_name = 'products_templates/unite_produit_confirm_delete.html'
    success_url = reverse_lazy('products_app:unite-produit-list')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Unité supprimée avec succès.')
        return response


# ============================================================
# API ProductLIST View
# ============================================================

from rest_framework import generics, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Products
from .serializers import ProductsSerializer

class ApiProductListView(generics.ListAPIView):
    queryset = Products.objects.all().select_related('categorie').prefetch_related("images")
    serializer_class = ProductsSerializer
    permission_classes = [AllowAny]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = ["categorie__nom", "nom", "stock"]
    
    search_fields = ['categorie__nom', "nom", "compatible_avec"]
    
    ordering_fields = ['prix', 'stock', 'nom']
    
    ordering = ['-id']


class ApiProductsdetail(generics.RetrieveAPIView):
    queryset = Products.objects.all().select_related('categorie', 'marque', 'unite').prefetch_related('images')
    serializer_class = ProductsSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'
    
class ApiProductsdetail(generics.RetrieveAPIView):
    """
    API publique pour récuprer les details d'un produits
    """
    queryset = Products.objects.all().select_related("categorie").prefetch_related("images")
    serializer_class = ProductsSerializer
    permission_classes = [AllowAny]
    lookup_field = "pk"