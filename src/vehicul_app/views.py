from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Vehicul
from .serializers import VehiculSerializer

from django.shortcuts import render, redirect
from django.views.generic import CreateView, ListView,DetailView, UpdateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from django.db.models import Q
from django.urls import reverse_lazy, reverse

from .models import Vehicul, Marque, VehiculeImage, TypeVehicule
from .forms import VehiculForm, MarqueForm, VehiculeImage, VehiculeImageFormSet, VehiculeImageForm, TypeVehiculeForm
from directeur_app.views import DirecteurDashboardView
from leads_app.forms import DemandeFinancementForm
from auth_app.models import kozUser


from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings
from chat_app.models import Message

import logging

logger = logging.getLogger(__name__)




############################ CRUD ERP MARQUE, TYPE VEHICULE, VEHICULES ############################
class ERP_CreateMarqueView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    
    model = Marque
    form_class = MarqueForm
    template_name = "directeur_templates/directeur.html"
    success_url = reverse_lazy("directeur_app:directeur-view")
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Nouvelle marque ajoutée")
        return response
            
        
    
    def form_invalid(self, form):
        dashboard = DirecteurDashboardView()
        dashboard.request = self.request
        context = dashboard.get_context_data()
        context["marque_form"] = form
        context["open_marque_modal"] = True
        return self.render_to_response(context)
    
class ERP_MarqueListView(LoginRequiredMixin, ListView):
    model = Marque
    template_name = "vehicul_templates/ERP/ERP_marque_list.html"
    context_object_name = "marque_list"

class ERP_MarqueDetailView(LoginRequiredMixin, DetailView):
    model = Marque
    template_name = "vehicul_templates/ERP/ERP_marque_detail.html"
    context_object_name = "marque"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "marque_form" not in context:
            context["marque_form"] = MarqueForm(instance=self.object)
        return context
    
class ERP_MarqueUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    
    model = Marque
    form_class = MarqueForm
    context_object_name = "marque"
    template_name = "vehicul_templates/ERP/ERP_marque_detail.html"
    
    def get_success_url(self):
        return reverse_lazy("vehicul_app:detail-marque", kwargs={"pk": self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Marque mise à jour avec succès")
        return response
    
    def form_invalid(self, form):
        dashboard = ERP_MarqueListView()
        dashboard.request = self.request
        dashboard.kwargs = self.kwargs
        dashboard.object = self.get_object()
        dashboard.object_list = self.get_queryset()
        context = dashboard.get_context_data()
        
        context["marque_form"] = form
        context["open_marque_modal"] = True
        return self.render_to_response(context)
       
class ERP_MarqueDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
        
    model = Marque
    template_name = "vehicul_templates/ERP/ERP_detail_marque.html"
    success_url = reverse_lazy("vehicul_app:list-marque")
        


############################# CRUD ERP TYPE VEHICULE ###########################################################
class ERP_CreateTypeVehiculeView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    
    model = TypeVehicule
    form_class = TypeVehiculeForm
    template_name = "directeur_templates/directeur.html"
    success_url = reverse_lazy("directeur_app:directeur-view")
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"✅ Type '{self.object.nom}' ajouté avec succès !")
        return response
    
    def form_invalid(self, form):
        dashboard = DirecteurDashboardView()
        dashboard.request = self.request
        context = dashboard.get_context_data()
        context["type_vehicul_form"] = form
        context["open_type_vehicul_modal"] = True
        return self.render_to_response(context)


class ERP_TypeVehiculeListView(LoginRequiredMixin, ListView):
    model = TypeVehicule
    template_name = "directeur_templates/directeur_type_vehicule_list.html"
    context_object_name = "types"


class ERP_TypeVehiculeDetailView(LoginRequiredMixin, DetailView):
    model = TypeVehicule
    template_name = "directeur_templates/directeur_type_vehicule_detail.html"
    context_object_name = "type_vehicule"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "update_type_vehicul_form" not in context:
            context["update_type_vehicul_form"]=TypeVehiculeForm(instance=self.object)
        return context


class ERP_TypeVehiculeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    
    model = TypeVehicule
    form_class = TypeVehiculeForm
    template_name = "vehicul_templates/type_vehicule_detail.html"
    success_url = reverse_lazy("vehicul_app:type-vehicul-list")
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"✅ Type '{self.object.nom}' mis à jour !")
        return response


class ERP_TypeVehiculeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    
    model = TypeVehicule
    template_name = "vehicul_templates/type_vehicule_confirm_delete.html"
    success_url = reverse_lazy("vehicul_app:type-vehicul-list")
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"✅ Type '{obj.nom}' supprimé avec succès !")
        return response



########################## CRUD ERP VEHICULES ###########################################################
class ERP_CreateVehiculView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    
    model = Vehicul
    form_class = VehiculForm
    template_name = "directeur_templates/directeur.html"
    success_url = reverse_lazy("directeur_app:directeur-view")
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Nouvelle voiture ajoutée")
        return response
        
    def form_invalid(self, form):
        dashboard = DirecteurDashboardView()
        dashboard.request = self.request
        context = dashboard.get_context_data()
        
        context["vehicul_form"] = form
        context["open_vehicul_modal"] = True
        return self.render_to_response(context)
        
    
class ERP_VehiculListView(LoginRequiredMixin, ListView):
    model = Vehicul
    context_object_name ="vehicul_list"
    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["partials/vehiculs/ERP_partials_vehicul_list.html"]
        
        return ["vehicul_templates/ERP/ERP_vehicul_list.html"]
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["marques"] = Marque.objects.all()
        context["TYPES_CARBURANT"] = Vehicul.TYPES_CARBURANT_CHOICES
        
        # ✅ Ajout de l'image principale pour chaque véhicule
        for vehicule in context["vehicul_list"]:
            image_principale = vehicule.images.filter(est_principale=True).first()
            vehicule.image_display = image_principale.image if image_principale else vehicule.image_principale
        
        return context
    
    def get_queryset(self):
        queryset = Vehicul.objects.all().select_related("marque").order_by("-date_ajout")
        
        search_query = self.request.GET.get("q")
        marque = self.request.GET.get("marque")
        carburant = self.request.GET.get("carburant")
        
        if search_query:
            queryset = queryset.filter(
                Q(modele__icontains=search_query) |
                Q(marque__nom__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(annee__icontains=search_query) |
                Q(carburant__icontains=search_query) |
                Q(kilometrage__icontains=search_query) |
                Q(prix__icontains=search_query)
            )
        
        if marque:
            queryset = queryset.filter(marque__nom=marque)
        
        if carburant:
            queryset = queryset.filter(carburant=carburant)
        
        return queryset
               
class ERP_VehiculDetailView(LoginRequiredMixin, DetailView):
    model = Vehicul
    template_name = "vehicul_templates/ERP/ERP_vehicul_detail.html"
    context_object_name = "vehicul"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Formulaire de modification
        if "vehicul_form" not in context:
            context["vehicul_form"] = VehiculForm(instance=self.object)
        
        # Formulaire de demande de financement
        initial = {"duree_mois": 36, "apport": 0}
        context["dmd_fin_form"] = DemandeFinancementForm(initial=initial)
        
        # ✅ Images du véhicule
        images = self.object.images.all().order_by('ordre', 'date_ajout')
        context["images"] = images
        
        # ✅ Image principale (fallback si pas trouvée)
        image_principal = images.filter(est_principale=True).first()
        if not image_principal and images.exists():
            image_principal = images.first()
        context["image_principal"] = image_principal
        
        return context

class ERP_VehiculUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    
    model = Vehicul
    form_class = VehiculForm
    template_name = "vehicul_templates/ERP/ERP_vehicul_detail.html"
    
    def get_success_url(self):
        return reverse_lazy("vehicul_app:detail-vehicul", kwargs={"pk": self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Voiture mise à jour avec succès")
        return response
    
    def form_invalid(self, form):
        dashboard = ERP_VehiculListView()
        dashboard.request = self.request
        dashboard.kwargs = self.kwargs
        dashboard.object = self.get_object()
        dashboard.object_list = self.get_queryset()
        context = dashboard.get_context_data()
        
        context["vehicul_form"] = form
        context["open_vehicul_modal"] = True
        return self.render_to_response(context)
    

class ERP_VehiculDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    
    model = Vehicul
    template_name = "vehicul_templates/ERP/ERP_vehicul_detail.html"
    success_url = reverse_lazy("vehicul_app:list-vehicul")
    

################################ ERP CRUD VEHICULE IMAGES ########################################################
class VehiculeImageListView(ListView):
    model = VehiculeImage
    template_name = "vehicul_templates/vehicul_images.html"
    context_object_name = "images"
    
    
    def get_queryset(self):
        self.vehicule = get_object_or_404(Vehicul, pk=self.kwargs['pk'])
        return self.vehicule.images.all().order_by('ordre', 'date_ajout')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vehicul'] = self.vehicule
        if "vehicul_image_form" not in context:
            context["vehicul_image_form"] = VehiculeImageForm()
        
        return context


@login_required
@require_POST
def ajouter_image(request, pk):
    vehicule = get_object_or_404(Vehicul, pk=pk)
    
    # ✅ Vérification des permissions
    if not (request.user.is_superuser or request.user.role == "directeur"):
        messages.error(request, "Vous n'avez pas la permission d'ajouter des images.")
        return redirect('vehicul_app:detail-vehicul', pk=vehicule.pk)
    
    # ✅ Traitement du formulaire
    form = VehiculeImageForm(request.POST, request.FILES)
    
    if form.is_valid():
        image = form.save(commit=False)
        image.vehicule = vehicule
        image.save()
        
        # ✅ Si c'est l'image principale, désactiver les autres
        if image.est_principale:
            VehiculeImage.objects.filter(
                vehicule=vehicule
            ).exclude(pk=image.pk).update(est_principale=False)
        
        messages.success(request, f"✅ Image ajoutée avec succès !")
    else:
        messages.error(request, f"❌ Erreur dans le formulaire : {form.errors}")
    
    # ✅ Redirection vers la page d'images
    return redirect('vehicul_app:vehicul-images-list', pk=vehicule.pk)
    
class VehiculeImageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = VehiculeImage
    template_name = "vehicul_templates/vehicul_image_confirm_delete.html"
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    
    def get_success_url(self):
        return reverse_lazy('vehicul_app:detail-vehicul', kwargs={'pk': self.object.vehicule.pk})
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, "Image supprimée avec succès !")
        return response
    

# ============================================================
# ✅ API
# ============================================================
class APIVehiculListView(generics.ListAPIView):
    """
    API publique pour récupérer tous les véhicules disponibles.
    Accessible sans authentification.
    """
    queryset = Vehicul.objects.all().select_related('marque').prefetch_related('images')
    serializer_class = VehiculSerializer
    permission_classes = [AllowAny]  # ✅ Tout le monde peut voir le catalogue
    
    # ✅ Filtres et recherche
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    
    # ✅ Champs sur lesquels on peut filtrer
    filterset_fields = [
        'marque__nom',
        'carburant',
        'annee',
        'disponible',
    ]
    
    # ✅ Champs sur lesquels on peut rechercher
    search_fields = [
        'marque__nom',
        'modele',
        'description',
    ]
    
    # ✅ Champs sur lesquels on peut trier
    ordering_fields = [
        'prix',
        'annee',
        'kilometrage',
        'date_ajout',
    ]
    ordering = ['-date_ajout']  # ✅ Tri par défaut

class APIVehiculDetailView(generics.RetrieveAPIView):
    """
    API publique pour récupérer les détails d'un véhicule.
    """
    queryset = Vehicul.objects.all().select_related('marque').prefetch_related('images')
    serializer_class = VehiculSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'




# ============================================================
# ✅ SITE PUBLIC : Vues pour l'affichage public des véhicules
# ============================================================

@login_required
def contacter_vehicule(request, vehicul_id):
    vehicule = get_object_or_404(Vehicul, id=vehicul_id)
    
    # ✅ Message pré-rempli
    message_content = f"""Bonjour,

    Je suis intéressé par le véhicule suivant :
    🚗 {vehicule.marque.nom} {vehicule.modele} ({vehicule.annee})
    📍 Prix : {vehicule.prix} FCFA
    🔗 Lien : {request.build_absolute_uri(reverse('vehicul_app:detail-vehicul', kwargs={'pk': vehicule.pk}))}

    Pouvez-vous me donner plus d'informations ?

    Cordialement,
    {request.user.nom_complet}"""

    # ✅ Envoyer dans le chat
    commerciaux = kozUser.objects.filter(role='commercial')
    for commercial in commerciaux:
        Message.objects.create(
            client=request.user,
            commercial=commercial,
            contenu=message_content,
            est_client=True
        )
    
    messages.success(request, f"✅ Votre message a été envoyé au commercial pour {vehicule.marque.nom} {vehicule.modele}")
    return redirect('chat_app:chat-view')

def detail_vehicul_slug(request, slug):
    vehicul = get_object_or_404(Vehicul, slug=slug)
    return redirect('vehicul_app:site-vehicul-detail', vehicul.pk)

class SITE_VehiculListView(ListView):
    """
    Vue publique pour afficher la liste des véhicules disponibles
    Accessible à tous sans authentification
    """
    model = Vehicul
    template_name = "vehicul_templates/SITE/SITE_vehicul_list.html"
    context_object_name = "vehicules"
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Vehicul.objects.filter(
            disponible=True
        ).select_related('marque', 'type_vehicule').prefetch_related('images').order_by('-date_ajout')
        
        # Filtres
        search_query = self.request.GET.get('q')
        marque = self.request.GET.get('marque')
        carburant = self.request.GET.get('carburant')
        type_vehicule = self.request.GET.get('type')
        
        if search_query:
            queryset = queryset.filter(
                Q(modele__icontains=search_query) |
                Q(marque__nom__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        if marque:
            queryset = queryset.filter(marque__pk=marque)
        
        if carburant:
            queryset = queryset.filter(carburant=carburant)
        
        if type_vehicule:
            queryset = queryset.filter(type_vehicule__pk=type_vehicule)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['marques'] = Marque.objects.all()
        context['types'] = TypeVehicule.objects.all()
        context['carburants'] = Vehicul.TYPES_CARBURANT_CHOICES
        context['search_query'] = self.request.GET.get('q', '')
        
        # Ajouter l'image principale pour chaque véhicule
        for vehicule in context['vehicules']:
            image_principale = vehicule.images.filter(est_principale=True).first()
            vehicule.image_display = image_principale.image if image_principale else vehicule.image_principale
        
        return context

class SITE_VehiculByTypeListView(ListView):
    """
    Vue publique pour afficher la liste des véhicules d'un type spécifique.
    """
    model = Vehicul
    template_name = "vehicul_templates/SITE/SITE_vehicul_type_list.html"
    context_object_name = "vehicules"
    paginate_by = 12

    def get_queryset(self):
        self.selected_type = get_object_or_404(TypeVehicule, pk=self.kwargs['type_pk'])
        queryset = Vehicul.objects.filter(
            disponible=True,
            type_vehicule=self.selected_type
        ).select_related('marque', 'type_vehicule').prefetch_related('images').order_by('-date_ajout')

        search_query = self.request.GET.get('q')
        marque = self.request.GET.get('marque')
        carburant = self.request.GET.get('carburant')

        if search_query:
            queryset = queryset.filter(
                Q(modele__icontains=search_query) |
                Q(marque__nom__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        if marque:
            queryset = queryset.filter(marque__pk=marque)

        if carburant:
            queryset = queryset.filter(carburant=carburant)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_type'] = self.selected_type
        context['marques'] = Marque.objects.all()
        context['carburants'] = Vehicul.TYPES_CARBURANT_CHOICES
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_marque'] = self.request.GET.get('marque', '')
        context['selected_carburant'] = self.request.GET.get('carburant', '')

        for vehicule in context['vehicules']:
            image_principale = vehicule.images.filter(est_principale=True).first()
            vehicule.image_display = image_principale.image if image_principale else vehicule.image_principale

        return context

from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

class SITE_VehiculDetailView(DetailView):
    model = Vehicul
    template_name = "vehicul_templates/SITE/SITE_vehicul_detail.html"
    context_object_name = "vehicul"

    def get_object(self):
        if 'pk' in self.kwargs:
            return get_object_or_404(Vehicul, pk=self.kwargs['pk'])
        elif 'slug' in self.kwargs:
            return get_object_or_404(Vehicul, slug=self.kwargs['slug'])
        raise Http404("Aucun véhicule trouvé")

    def get_queryset(self):
        return Vehicul.objects.select_related('marque', 'type_vehicule').prefetch_related('images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicule = self.object
        # === TOUT TON CONTEXTE EXISTANT ===
        images = vehicule.images.all().order_by('ordre', 'date_ajout')
        context['images'] = images

        image_principal = images.filter(est_principale=True).first()
        if not image_principal and images.exists():
            image_principal = images.first()
        context['image_principal'] = image_principal

        if self.request.user.is_authenticated:
            initial = {"duree_mois": 36, "apport": 0}
            context['dmd_fin_form'] = DemandeFinancementForm(initial=initial)

        context['vehicules_similaires'] = Vehicul.objects.filter(
            marque=vehicule.marque,
            disponible=True
        ).exclude(pk=vehicule.pk)[:4]

        paginator = Paginator(images, 1)
        page_number = self.request.GET.get('page', 1)
        vehicule_imgs_page = paginator.get_page(page_number)

        context['vehicule_imgs_page'] = vehicule_imgs_page
        context['total_page'] = paginator.num_pages
        context['current_page'] = page_number
        context['direction'] = self.request.GET.get('direction', 'right')

        return context
    
class SITE_MarqueListeView(ListView):
 
    """
    Vue publique pour afficher la liste des marques
    """
    model = Marque
    template_name = "vehicul_templates/SITE/SITE_marque_list.html"
    context_object_name = "marques"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter le nombre de véhicules par marque
        for marque in context['marques']:
            marque.nombre_vehicules = marque.vehicul.filter(disponible=True).count()
        return context

class SITE_MarqueDetailView(DetailView):
    """
    Vue publique pour afficher les détails d'une marque et ses véhicules
    """
    model = Marque
    template_name = "vehicul_templates/SITE/SITE_marque_detail.html"
    context_object_name = "marque"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Tous les véhicules de cette marque
        context['vehicules'] = Vehicul.objects.filter(
            marque=self.object,
            disponible=True
        ).select_related('type_vehicule').prefetch_related('images').order_by('-date_ajout')
        
        # Ajouter l'image principale
        for vehicule in context['vehicules']:
            image_principale = vehicule.images.filter(est_principale=True).first()
            vehicule.image_display = image_principale.image if image_principale else vehicule.image_principale
        
        # Autres marques (suggestions)
        context['autres_marques'] = Marque.objects.exclude(pk=self.object.pk)[:6]
        
        return context
    
def vehicul_image_partials(request, vehicul_id):
    vehicule = get_object_or_404(Vehicul, pk=vehicul_id)
    vehicule_imgs = vehicule.images.all()
    
    # ✅ Pagination : 1 image par page
    paginator = Paginator(vehicule_imgs, 1)
    page_number = request.GET.get("page", 1)
    vehicule_imgs_page = paginator.get_page(page_number)
    
    direction = request.GET.get('direction', 'right')
    
    return render(request, 'partials/vehiculs/vehicul_detail_images.html', {
        'vehicule_imgs_page': vehicule_imgs_page,
        'total_page': paginator.num_pages,
        'current_page': page_number,
        'direction': direction,
        'vehicul': vehicule,
    })


def toggle_favori(request, vehicul_id):
    if request.user.is_anonymous or request.user.role != 'client':
        response = render(request, "partials/vehiculs/_favori_result.html", {
            "success": False,
            "title": "❌ Action non autorisée",
            "message": "Seuls les clients ou abonnée peuvent ajouter des favoris.",
        })
        return response
    
    vehicul = get_object_or_404(Vehicul, id=vehicul_id)
    
    if vehicul.favoris_de.filter(id=request.user.id).exists():
        vehicul.favoris_de.remove(request.user)
        ajoute = False
    else:
        vehicul.favoris_de.add(request.user)
        ajoute = True
    
        Message.objects.create(
            client=request.user,
            commercial=None,  # message système, pas encore pris en charge par un commercial précis
            contenu=(
                    f"Vous avez ajouté {vehicul.marque.nom} {vehicul.modele} à vos favoris. "
                    f"N'hésitez pas à échanger avec un conseiller sur les options de financement disponibles."
            ),
            est_client=False,
            lu=False,
            origine_automatique=True,
            )

        if request.user.email:
            try:
                lien_chat = request.build_absolute_uri(reverse('chat_app:chat-view'))
                html_message = render_to_string('emails/vehicul/vehicul_notif_favori.html', {
                        'client': request.user,
                        'vehicule': f"{vehicul.marque.nom} {vehicul.modele}",
                        'lien_chat': lien_chat,
                })
                send_mail(
                        subject=f"💬 Nouveau message concernant {vehicul.marque.nom} {vehicul.modele}",
                        message=strip_tags(html_message),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[request.user.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
            except Exception as e:
                logger.error(f"Erreur email notif favori pour {request.user.email}: {e}")
        
        
    return render(request, "partials/vehiculs/_favori_button.html", {"vehicul": vehicul})
        
        