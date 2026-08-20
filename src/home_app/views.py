import django
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect,render
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.urls import reverse, reverse_lazy
from auth_app.models import kozUser
from home_app.forms import ActualiteForm, AvisReseauForm, TemoignageTextuelForm, VideoTemoignageForm
from vehicul_app.models import Vehicul, TypeVehicule
from services_app.models import Services, TypesServices
from products_app.models import Products
from .models import Actualite, Temoignage, AvisReseau, VideoTemoignage



def home_page_view(request):
    """
    Affiche la page d'accueil HTML
    C'est une vue Django classique, pas une API
    """
    
    #Récuperer tout les vehicules en vedettes
    vehicules_vedette = Vehicul.objects.filter(est_vedette = True).annotate(nb_favoris=Count('favoris_de')).order_by('-nb_favoris')
    
    
    
    # paginator 1 véhicule par page
    paginator = Paginator(vehicules_vedette, 1)
    page_number = request.GET.get('page', 1)
    vehicules_page = paginator.get_page(page_number)
    ctx = {
        "vehicules": Vehicul.objects.all(),
        "vehicules_vedette": vehicules_vedette,
        "vehicules_page":vehicules_page,
        "total_pages":paginator.num_pages,
        "current_page":page_number,
        "types_vehicule" : TypeVehicule.objects.all(),
        "services_vedette": Services.objects.filter(est_vedette = True),
        "produits_vedette": Products.objects.filter(est_vedette = True, est_disponible = True),
        "nouveaux_produits": Products.objects.filter(est_disponible = True,est_nouveau = True),
        "temoignages": Temoignage.objects.filter(est_approuve = True).order_by('-date_creation')[:5],
        "avis_reseaux": AvisReseau.objects.filter(est_actif = True).order_by('-date_publication'),
        "videos": VideoTemoignage.objects.filter(est_actif = True).order_by('-date_ajout')[:5],
        "temoignage_textuel_form": TemoignageTextuelForm(),
        "actualites": Actualite.objects.filter(est_vedette = True).order_by('-date_publication'),
        "likes": Vehicul.objects.annotate(nb_favoris=Count('favoris_de')).order_by('-nb_favoris')
    }
    return render(request, "home_templates/home_page.html", ctx)


def vehicules_partial(request):
    """
    Vue HTMX pour charger les véhicules paginés
    """
    vehicules_vedette = Vehicul.objects.filter(est_vedette=True).annotate(nb_favoris=Count('favoris_de')).order_by('-nb_favoris')
    paginator = Paginator(vehicules_vedette, 1)
    page_number = request.GET.get('page', 1)
    vehicules_page = paginator.get_page(page_number)
    return render(request, "partials/vehiculs/vehicul_vedette_gallery.html", {
            "vehicules_page":vehicules_page,
            "total_page": paginator.num_pages,
            "current_page":page_number
        }
    )


class TextuelTemoignageCreateView(CreateView):
    model = Temoignage
    template_name = 'home_templates/temoignage_textuel_form.html'
    form_class = TemoignageTextuelForm
    def form_valid(self, form):
        time.sleep(1.3)
        response = render(self.request, "partials/site/_site_result.html",{"success": True,
                                                                                "titre" : "👍🏽 Enregistré ",
                                                                                "message" : "✅ Merci pour votre témoignage ! Il sera visible après approbation.",
                                                                                "reload_on_close" : False
                                                                                })
        response['HX-Trigger']= "closeHomeModal"
        return response
    
    
    # Redirige vers la page d'accueil après la soumission du formulaire

class TemoignageTextuelListView(LoginRequiredMixin, ListView):
    model = Temoignage
    template_name = 'directeur_templates/temoignages_textuel_list.html'
    context_object_name = 'temoignages'
    paginate_by = 10


    def get_queryset(self):
        queryset = Temoignage.objects.all().order_by('-date_creation')
        
        # Filtres
        statut = self.request.GET.get('statut')
        if statut == 'approuve':
            queryset = queryset.filter(est_approuve=True)
        elif statut == 'en_attente':
            queryset = queryset.filter(est_approuve__isnull=True)
        elif statut == 'rejete':
            queryset = queryset.filter(est_approuve=False)
        
        source = self.request.GET.get('source')
        if source:
            queryset = queryset.filter(source=source)
        
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(nom__icontains=q) | 
                Q(prenom__icontains=q) | 
                Q(message__icontains=q)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['source_choices'] = Temoignage.SOURCE_CHOICES
        # Statistiques
        context['temoignages_stats'] = {
            'approuves': Temoignage.objects.filter(est_approuve=True).count(),
            'en_attente': Temoignage.objects.filter(est_approuve__isnull=True).count(),
            'rejetes': Temoignage.objects.filter(est_approuve=False).count(),
        }
        return context

    
@login_required
def approuver_temoignage(request, temoignage_id):
    temoignage = get_object_or_404(Temoignage, pk=temoignage_id)
    temoignage.est_approuve = True
    temoignage.save()
    messages.success(request, f"✅ Témoignage de {temoignage.prenom} {temoignage.nom} approuvé !")
    return redirect('home_app:temoignages-textuel-list')


@login_required
def rejeter_temoignage(request, temoignage_id):
    temoignage = get_object_or_404(Temoignage, pk=temoignage_id)
    temoignage.est_approuve = False
    temoignage.save()
    messages.warning(request, f"❌ Témoignage de {temoignage.prenom} {temoignage.nom} rejeté.")
    return redirect('home_app:temoignages-textuel-list')


@login_required
def delete_textuel_temoignage(request, pk):
    temoignage = get_object_or_404(Temoignage, pk=pk)
    temoignage.delete()
    messages.success(request, f"🗑️ Témoignage de {temoignage.prenom} {temoignage.nom} supprimé avec succès.")
    return redirect('home_app:temoignages-textuel-list')
    

class CreateAvisReseauView(LoginRequiredMixin, CreateView):
    model = AvisReseau
    template_name = 'directeur_templates/avis_reseau_form.html'
    form_class = AvisReseauForm
    def get_success_url(self):
        return reverse_lazy('directeur_app:directeur-view')  # Redirige vers la page d'accueil après la soumission du formulaire
    
    def form_valid(self, form):
        messages.success(self.request, "✅ Avis ajouté avec succès !")
        return super().form_valid(form)

class ListeAvisReseauView(LoginRequiredMixin, ListView):
    model = AvisReseau
    template_name = 'directeur_templates/avis_reseau_list.html'
    context_object_name = 'avis_reseaux'

    def get_queryset(self):
        queryset = AvisReseau.objects.all().order_by('-date_publication')
        
        # Filtres
        reseau = self.request.GET.get('reseau')
        if reseau:
            queryset = queryset.filter(reseau=reseau)
        
        statut = self.request.GET.get('statut')
        if statut == 'actif':
            queryset = queryset.filter(est_actif=True)
        elif statut == 'inactif':
            queryset = queryset.filter(est_actif=False)
        
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(nom_utilisateur__icontains=q) |
                Q(message__icontains=q)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reseau_choices'] = AvisReseau.RESEAUX_CHOICES
        context['avis_actifs'] = AvisReseau.objects.filter(est_actif=True).count()
        context['avis_inactifs'] = AvisReseau.objects.filter(est_actif=False).count()
        return context


@login_required
def activer_avis_reseau(request, avis_id):
    avis = get_object_or_404(AvisReseau, id=avis_id)
    avis.est_actif = True
    avis.save()
    messages.success(request, f"✅ Avis de {avis.nom_utilisateur} activé !")
    return redirect('home_app:avis-reseau-list')


@login_required
def desactiver_avis_reseau(request, avis_id):
    avis = get_object_or_404(AvisReseau, id=avis_id)
    avis.est_actif = False
    avis.save()
    messages.warning(request, f"❌ Avis de {avis.nom_utilisateur} désactivé.")
    return redirect('home_app:avis-reseau-list')
    
class VideoTemoignageListView(ListView):
    model = VideoTemoignage
    template_name = 'directeur_templates/video_temoignages_list.html'
    context_object_name = 'video_temoignages'
    paginate_by = 5  # Nombre de vidéos par page

    def get_queryset(self):
        return VideoTemoignage.objects.all().order_by('-date_ajout')
    
class VideoTemoingnageCreateView(LoginRequiredMixin, CreateView):
    model = VideoTemoignage
    template_name = 'directeur_templates/video_temoignage_form.html'
    form_class = VideoTemoignageForm
    
    def get_success_url(self):
        return reverse_lazy('directeur_app:directeur-view')  # Redirige vers la page d'accueil après la soumission du formulaire


class ActualiteListView(LoginRequiredMixin, ListView):
    model = Actualite
    template_name = 'directeur_templates/actualites_list.html'
    context_object_name = 'actualites'

    def get_queryset(self):
        return Actualite.objects.all().order_by('-date_publication', '-date_evenement')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'actualite_form' not in context:
            context['actualite_form'] = ActualiteForm()
        return context


class ActualiteDetailView(LoginRequiredMixin, DetailView):
    model = Actualite
    template_name = 'directeur_templates/actualite_detail.html'
    context_object_name = 'actualite'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if 'actualite_form' not in context:
            context['update_actualite_form'] = ActualiteForm(instance=self.object)  # Pré-remplir le formulaire avec l'actualité actuelle
        return context
    
    def get_success_url(self):
        return reverse_lazy('home_app:actualites-list')  # Redirige vers la liste des actualités après la soumission du formulaire


class ActualiteCreateView(LoginRequiredMixin, CreateView):
    model = Actualite
    form_class = ActualiteForm
    template_name = 'directeur_templates/actualite_form.html'

    def get_success_url(self):
        return reverse_lazy('home_app:actualites-list')


class ActualiteUpdateView(LoginRequiredMixin, UpdateView):
    model = Actualite
    form_class = ActualiteForm
    success_url = reverse_lazy('home_app:actualites-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"✅ Actualité '{self.object.titre}' modifiée avec succès !")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "❌ Erreur dans le formulaire. Vérifiez les champs.")
        return super().form_invalid(form)
    def get_success_url(self):
        return reverse_lazy('home_app:actualites-list')  # Redirige vers la liste des actualités après la soumission du formulaire


@login_required
def delete_actualite(request, pk):
    """FBV pour supprimer une actualité"""
    actualite = get_object_or_404(Actualite, pk=pk)
    titre = actualite.titre
    actualite.delete()
    messages.success(request, f"✅ Actualité '{titre}' supprimée avec succès !")
    return redirect('home_app:actualites-list')


# home_app/views.py

from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import RendezVous
import time

def contact_form(request):
    time.sleep(1.5)
    if request.method == 'POST':
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        sujet = request.POST.get('sujet')
        message = request.POST.get('message')
        
        context = {
            'nom': nom,
            'email': email,
            'telephone': telephone,
            'sujet': sujet,
            'message': message,
        }
        
        html_message = render_to_string('emails/contact/contact.html', context)
        plain_message = strip_tags(html_message)
        commerciaux = kozUser.objects.filter(role='commercial', is_active=True)
        for commercial in commerciaux:
            send_mail(
                subject=f"📩 Nouveau message de {nom} - {sujet}",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[commercial.email],
                html_message=html_message,
                fail_silently=False,
            )
            
        return render(request, "partials/contact/contact_result.html",{
            'success': True,
            'title': '✅ Envoyé',
            'message': "Votre message à été envoyé,Un commercial vous contactera sous 24h.",
            
        })
        
       


def prise_rdv(request):
    
    time.sleep(1.5)
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        telephone = request.POST.get('telephone')
        date = request.POST.get('date')
        heure = request.POST.get('heure')
        motif = request.POST.get('motif')
        
        
        # Créer le rendez-vous
        rendez_vous = RendezVous.objects.create(
            client=request.user if request.user.is_authenticated else None,
            nom = nom if nom else None,
            prenom = prenom if prenom else None,
            telephone = telephone if telephone else None,
            date_rendez_vous=f"{date} {heure}",
            motif=motif,
            statut='en_attente'
        )
        
        if rendez_vous:
            return render(request, "partials/contact/contact_result.html",{
            'success': True,
            'title': '✅ Enregisté',
            'message': f"""Votre rendez-vous du {date} à {heure} a été enregistré.
                            Un commercial vous contactera sous 24h."""
        })
    return redirect(request, 'home_app:home-page')

