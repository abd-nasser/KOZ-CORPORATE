from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from leads_app.utils import generer_echeances_offre, generer_echeances_demande
from datetime import datetime


from django.urls import reverse_lazy, reverse
from django.conf import settings

from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.views.generic import TemplateView, ListView, DetailView, CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from decimal import Decimal


from auth_app.models import kozUser
from client_app.views import ClientDetailView
from client_app.models import Documents
from leads_app.models import Vente, demande_financement, PaiementFinancement
from client_app.models import Maintenance
from commercial_app.models import Offre
from chat_app.models import Message
from products_app.models import Products
from home_app.models import RendezVous


from auth_app.forms import UserRegisterForm, ChangePasswordForm
from leads_app.forms import GestionFinancementForm, DocumentsUploadForm, VenteSimpleForm
from client_app.forms import MaintenanceForm
from .forms import OffreFinancementForm, OffreSimpleForm

import logging
import time
from django.db import transaction

logger = logging.getLogger(__name__)



@login_required
def creer_offre(request, demande_id=None):
    demande = get_object_or_404(demande_financement, id=demande_id)
    
    if request.user.role not in ['commercial', 'directeur']:
        messages.error(request, "Vous n'avez pas l'autorisation de créer une offre.")
        return redirect('leads_app:detail-demande', demande.pk)
    
    if hasattr(demande.client, 'offre'):
        messages.warning(request, "Une offre existe déjà pour ce client.")
        return redirect('commercial_app:offre-detail', demande.client.offre.id)
    
    if request.method == 'POST':
        form = OffreFinancementForm(request.POST)
        if form.is_valid():
            offre = form.save(commit=False)
            offre.client = demande.client
            offre.demande_financement = demande
            offre.prix_vehicule = form.cleaned_data['prix_vehicule']
            offre.apport_demande = form.cleaned_data['apport_demande']
            offre.montant_finance = offre.prix_vehicule - offre.apport_demande
            offre.mensualite = (offre.montant_finance * (offre.taux_interet / 100 / 12)) / (1 - (1 + offre.taux_interet / 100 / 12) ** -offre.duree_mois)
            offre.type_offre = "demande"
            offre.statut = "envoyee"
            offre.save()
            
            # ✉️ EMAIL AU CLIENT
            try:
                context_email = {
                    'client': demande.client,
                    'offre_id': offre.id,
                    'vehicule': str(offre.vehicule_propose) if offre.vehicule_propose else "Véhicule sélectionné",
                    'montant_finance': offre.montant_finance,
                    'mensualite': offre.mensualite,
                    'duree_mois': offre.duree_mois,
                    'apport': offre.apport_demande,
                    'date_expiration': offre.date_expiration,
                    'lien_offre': request.build_absolute_uri(f"/client/offres/{offre.id}/"),
                }
                html_message = render_to_string('emails/offres/offre_creee_client.html', context_email)
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject="📄 Une offre de financement vous attend - KOZ Services",
                    message=plain_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[demande.client.email],
                    html_message=html_message,
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Erreur envoi email au client: {e}")
            
            messages.success(request, f"Offre créée et envoyée à {demande.client.nom_complet}.")
            
            # Redirection selon le rôle
            if request.user.role == 'commercial':
                return redirect('commercial_app:offre-detail', offre.pk)
            else:
                return redirect('directeur_app:offre-detail', offre.pk)
        else:
            # Formulaire invalide
            template = 'commercial_templates/commercial_demande_detail.html' if request.user.role == 'commercial' else 'directeur_templates/directeur_demande_detail.html'
            return render(request, template, {
                'demande': demande,
                'offre_form': form,
                'gestion_type_fin_form': GestionFinancementForm(instance=demande),
                'open_offre_modal': True
            })
    
    return redirect('leads_app:detail-demande', demande.pk)

@login_required
def accepter_offre(request, offre_id):
    time.sleep(1.5)
    if request.user.role != "client":
        messages.error(request, "Vous n'etes pas autorisé à exectuer cette action")
        return redirect("client_app:client-view")
    
    offre = get_object_or_404(Offre, id=offre_id, client=request.user)
    
    if offre.statut != 'envoyee':
        response = render(request, 'partials/offre/_offres_result.html', {
            'success': False,
            'title': '❌ Action impossible',
            'message': "Cette offre ne peut pas être acceptée.",
            'reload_on_close': False,
        })
        response['HX-Trigger'] = 'closeOffreGestionModal'
        return response

    with transaction.atomic():
        offre.statut = 'acceptee'
        offre.save()


        vente = None
        if offre.type_offre == "simple":
            vente = Vente.objects.create(
                client=request.user,
                vehicul=offre.vehicule_propose,
                statut="gestion_de_statut",
                montant=offre.montant_propose,
                montant_total_paye = offre.montant_propose,
                offre=offre,
            )

    commerciaux = kozUser.objects.filter(role='commercial')
    emails = [c.email for c in commerciaux if c.email]
    if emails:
        try:
            for commercial in commerciaux:
                if not commercial.email:
                    continue
                context_email = {
                    'client': offre.client,
                    'offre_id': offre.id,
                    'date_acceptation': timezone.now(),
                    'vehicule': str(offre.vehicule_propose) if offre.vehicule_propose else "Véhicule sélectionné",
                    'montant_finance': offre.montant_finance,
                    'lien_vente': request.build_absolute_uri(vente.get_absolute_url()) if vente else None,
                    'lien_client': request.build_absolute_uri(offre.client.get_absolute_url()),
                    'commercial': commercial,
                }
                html_message = render_to_string('emails/offres/offre_acceptee_commercial.html', context_email)
                plain_message = strip_tags(html_message)
                send_mail(
                    subject="✅ Un client a accepté son offre - KOZ Services",
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[commercial.email],
                    html_message=html_message,
                    fail_silently=False,
                )
        except Exception as e:
            logger.error(f"Erreur envoi email: {e}")

    response = render(request, 'partials/offre/_offres_result.html', {
        'success': True,
        'title': '✅ Offre acceptée',
        'message': "L'offre a été acceptée et le commercial a été notifié.",
        'reload_on_close': True,
    })
    response['HX-Trigger'] = 'closeOffreGestionModal'
    return response
    
@login_required
def refuser_offre(request, offre_id):
    time.sleep(1.5)
    if request.user.role != "client":
        messages.error(request, "Vous n'etes pas autorisé à exectuer cette action")
        return redirect("client_app:client-view")
    
    offre = get_object_or_404(Offre, id=offre_id, client=request.user)
    
    if offre.statut != 'envoyee':
        response = render(request, 'partials/offre/_offres_result.html', {
                'success': False,
                'title': '❌ Action impossible',
                'message': "Cette offre ne peut pas être refusée.",
                'reload_on_close': False,
        })
        response['HX-Trigger'] = 'closeOffreGestionModal'
        return response
        
    
    offre.statut = 'refusee'
    offre.save()
    
    # ✉️ Email à tous les commerciaux
    commerciaux = kozUser.objects.filter(role='commercial')
    if commerciaux.exists():
        try:
            for commercial in commerciaux:
                if not commercial.email:
                    continue
                context_email = {
                    'client': offre.client,
                    'offre_id': offre.id,
                    'vehicule': str(offre.vehicule_propose) if offre.vehicule_propose else "Non renseigné",
                    'date_refus': timezone.now(),
                    'lien_client': request.build_absolute_uri(offre.client.get_absolute_url()),
                    'commercial': commercial,
                }
                html_message = render_to_string('emails/offres/offre_refusee_commercial.html', context_email)
                plain_message = strip_tags(html_message)
                send_mail(
                    subject="❌ Un client a refusé son offre - KOZ Services",
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[commercial.email],
                    html_message=html_message,
                    fail_silently=False,
                )
        except Exception as e:
            logger.error(f"Erreur envoi email au commercial: {e}")
    
   
    response = render(request, 'partials/offre/_offres_result.html', {
            'success': True,
            'title': '❌ Offre refusée',
            'message': "L'offre a été refusée et le commercial a été notifié.",
            'reload_on_close': True,
        })
    response['HX-Trigger'] = 'closeOffreGestionModal'
    return response
   
@login_required
def negocier_offre(request, offre_id):
    time.sleep(1.5)
    if request.user.role != "client":
        messages.error(request, "Vous n'etes pas autorisé à exectuer cette action")
        return redirect("client_app:client-view")
        
    offre = get_object_or_404(Offre, id=offre_id, client=request.user)
    
    if offre.statut != 'envoyee':
        response = render(request, 'partials/offre/_offres_result.html', {
                'success': False,
                'title': '❌ Action impossible',
                'message': "Seules les offres envoyées peuvent être renégociées.",
                'reload_on_close': False,
            })
        response['HX-Trigger'] = 'closeOffreGestionModal'
        return response
        
    
    # 1️⃣ Changer le statut de l'offre
    offre.statut = 'brouillon'
    offre.save()
    
    # 2️⃣ 📨 Email à tous les commerciaux
    commerciaux = kozUser.objects.filter(role='commercial')
    if commerciaux.exists():
        try:
            for commercial in commerciaux:
                if not commercial.email:
                    continue
                context_email = {
                    'client': offre.client,
                    'offre_id': offre.id,
                    'vehicule': str(offre.vehicule_propose) if offre.vehicule_propose else "Non renseigné",
                    'montant_finance': offre.montant_finance,
                    'date_demande': timezone.now(),
                    'lien_offre': request.build_absolute_uri(offre.get_absolute_url()),
                    'lien_client': request.build_absolute_uri(offre.client.get_absolute_url()),
                    'commercial': commercial,
                }
                html_message = render_to_string('emails/offres/offre_negociation_commercial.html', context_email)
                plain_message = strip_tags(html_message)
                send_mail(
                    subject="🔄 Demande de renégociation d'offre - KOZ Services",
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[commercial.email],
                    html_message=html_message,
                    fail_silently=False,
                )
        except Exception as e:
            logger.error(f"Erreur envoi email au commercial: {e}")
    
    
    
    
    response = render(request, 'partials/offre/_offres_result.html', {
            'success': True,
            'title': '🔄 Renégociation demandée',
            'message': "Votre demande de renégociation a été envoyée au commercial.",
            'reload_on_close': True,
        })
    response['HX-Trigger'] = 'closeOffreGestionModal'
    return response

   
class CommercialClientListFilter(LoginRequiredMixin, UserPassesTestMixin, ListView):  
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff or self.request.user.role in ['directeur', 'commercial']
    
    model = kozUser
    context_object_name = "clients"
    template_name = "partials/client/partials_client_list.html"
    def get_queryset(self):
        queryset = kozUser.objects.filter(role="client")
        q = self.request.GET.get("q", "")
        if q:
                queryset = queryset.filter(
                    Q(nom_complet__icontains=q) |Q(email__icontains=q)|
                    Q(telephone__icontains=q)|Q(pays__icontains=q)|Q(ville__icontains=q)|
                    Q(genre__icontains=q)
                )
        
        
        return queryset.order_by('-date_inscription')

class CommercialDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    
    template_name = "commercial_templates/commercial.html"
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.role == "commercial"
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["commercial"] = self.request.user
        
        # === FORMULAIRES ===
        if "user_register_form" not in context:
            context["user_register_form"] = UserRegisterForm()
        
        if 'change_pass_form' not in context:
            context["change_pass_form"] = ChangePasswordForm()
        
        # ========================================
        # ✅ 1. TOUS LES CLIENTS
        # ========================================
        tous_les_clients = kozUser.objects.filter(role="client")
        
        
        context["clients"]= tous_les_clients
        # ========================================
        # ✅ 2. STATISTIQUES
        # ========================================
        context['demande_financement_en_cours'] = demande_financement.objects.filter(
            client__in=tous_les_clients,
            etape="en_cours"
        ).count()
        
        context["offres_acceptees"] = Offre.objects.filter(
            client__in=tous_les_clients,
            statut="acceptee"
        ).count()
        
        context["maintenance_planifiee"] = Maintenance.objects.filter(
            client__in=tous_les_clients,
            statut="planifiee"
        ).count()
        
        context['produits_stock_faible'] = Products.objects.filter(stock__lte=5).order_by('stock')
        context["demande_rendez_vous"] = RendezVous.objects.filter(statut="en_attente").count()
        # ========================================
        # ✅ 3. TOTAL DES NON-LUS (via la propriété)
        # ========================================
        context["total_non_lus"] = sum(c.nb_messages_non_lus for c in tous_les_clients)
        
        return context


##########################################________________OFFRE_VIEW_________________####################################################
class OffreSimpleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role in ["commercial", "directeur"]
    
    model = Offre
    form_class = OffreSimpleForm  # ← Utilise le formulaire complet
    template_name = "clients_templates/client_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "offre_simple_form" not in context:
            context["offre_simple_form"] = OffreSimpleForm()
        return context
    
    def form_valid(self, form):
        time.sleep(3)
        client_id = self.kwargs.get("pk")
        client = get_object_or_404(kozUser, id=client_id)
        
        offre = form.save(commit=False)
        offre.client = client
        offre.type_offre = "simple"
        offre.statut = "envoyee"
        offre.save()
        
        # ✉️ Email au client
        try:
            context_email = {
                'client': client,
                'offre_id': offre.id,
                'montant_propose': offre.montant_propose,
                'vehicule': str(offre.vehicule_propose) if offre.vehicule_propose else "Véhicule sélectionné",
                'date_expiration': offre.date_expiration,
                'lien_offre': self.request.build_absolute_uri(offre.get_absolute_url()),
            }
            html_message = render_to_string('emails/offres/simple_offre.html', context_email)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject="📄 Une offre vous attend - KOZ Services",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Erreur envoi email au client: {e}")
        
        response = render(self.request, "partials/offre/_offres_result.html",{
                                            "success": True,
                                            "title": "✅ Offre envoyé ",
                                            "message": f"Offre simple créée pour {client.nom_complet}. Un email a été envoyé.",
                                            "reload_on_close":True
                                        })
        response['HX-Trigger'] = "closeOffreSimpleModal"
        return response
    
    def form_invalid(self, form):
        time.sleep(3)
        return render(self.request, "partials/offre/_offre_simple_form_error.html", {"offre_simple_form":form})
    
class OffreDeFinancementView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role in ["commercial", "directeur"]
    
    model = Offre
    form_class = OffreFinancementForm
    template_name = "clients_templates/client_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "offre_financement_form" not in context:
            context["offre_financement_form"] = OffreFinancementForm()  # ← CORRIGÉ
        return context
    
    def form_valid(self, form):
        time.sleep(3)
        client_id = self.kwargs.get('pk')
        client = get_object_or_404(kozUser, id=client_id)
        
        offre = form.save(commit=False)
        offre.client = client
        offre.type_offre = "offre_financement"
        offre.statut = "envoyee"
        
        # Récupérer les valeurs
        prix_vehicule = form.cleaned_data.get('prix_vehicule')
        apport_demande = form.cleaned_data.get('apport_demande')
        offre.montant_finance = prix_vehicule - (apport_demande or 0)
        
        # ✅ Calcul mensualité sécurisé
        if offre.taux_interet and offre.taux_interet > 0:
            taux_mensuel = offre.taux_interet / 100 / 12
            offre.mensualite = (
                (offre.montant_finance * taux_mensuel) / 
                (1 - (1 + taux_mensuel) ** -(offre.duree_mois or 1))
            )
        else:
            offre.mensualite = offre.montant_finance / (offre.duree_mois or 1)
        
        # ✅ Calcul total dû
        offre.total_du = (
            (offre.mensualite or 0) * (offre.duree_mois or 0)
            + (offre.frais_dossier or 0)
            + (offre.frais_garantie or 0)
        )
        
        offre.save()
        
        # ✉️ Email au client
        try:
            context_email = {
                'client': client,
                'offre_id': offre.id,
                'vehicule': str(offre.vehicule_propose) if offre.vehicule_propose else "Véhicule sélectionné",
                'montant_finance': offre.montant_finance,
                'mensualite': offre.mensualite,
                'duree_mois': offre.duree_mois,
                'apport': offre.apport_demande,
                'date_expiration': offre.date_expiration,
                'lien_offre': self.request.build_absolute_uri(offre.get_absolute_url())
            }
            html_message = render_to_string('emails/offres/offre_financement_cree_client.html', context_email)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject="📄 Une offre de financement vous attend - KOZ Services",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Erreur envoi email au client: {e}")
        
        response = render(self.request, "partials/offre/_offres_result.html",{
                                    "success": True,
                                    "title": "✅ Offre envoyé ",
                                    "message": f"Offre de financement créée pour {client.nom_complet}. Un email a été envoyé.",
                                    "reload_on_close":True
                                })
        response['HX-Trigger'] = "closeOffreModal"
        return response
        
       
    
    def form_invalid(self, form):
        time.sleep(3)
        return render(self.request, 'partials/offre/_offre_financement_form_errors.html', {'offre_financement_form': form})
        
class OffreView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    def test_func(self):
        return self.request.user.role in ['directeur', 'commercial', 'client']
    model = Offre
    context_object_name = "offres"
    def get_template_names(self):
        is_htmx = self.request.headers.get('HX-Request') == 'true'
        if self.request.user.role == "commercial" and self.request.user.is_staff:
            return ["partials/offre/partials_offre_list.html" if is_htmx else "commercial_templates/commercial_offre_list.html"]
        
        elif self.request.user.role == "directeur":
            return ["partials/offre/partials_offre_list.html" if is_htmx else "directeur_templates/directeur_offre_list.html"]
        
        return ["partials/offre/partials_offre_list.html" if is_htmx else "clients_templates/clients_offre_list.html"]
    
    def get_queryset(self):
        if self.request.user.role == "directeur":
            queryset = Offre.objects.all()
            q = self.request.GET.get("q")
            statut = self.request.GET.get("statut")
            if q:
                queryset = queryset.filter(
                    Q(client__nom_complet__icontains=q) |Q(client__email__icontains=q)|
                    Q(vehicule_propose__marque__nom__icontains=q)|
                    Q(vehicule_propose__modele__icontains=q)|
                    Q(vehicule_propose__annee__icontains=q)
                )
            if statut:
                queryset = queryset.filter(statut=statut)
                
            return queryset.order_by("-date_creation")
            
        elif self.request.user.role == "commercial" or (self.request.user.is_staff and not self.request.user.is_superuser):
            queryset = Offre.objects.all().select_related("client")
            q = self.request.GET.get("q")
            statut = self.request.GET.get("statut")
            type_offre = self.request.GET.get("type_offre")
            if q:
                queryset = queryset.filter(
                    Q(client__nom_complet__icontains=q) |Q(client__email__icontains=q)|
                    Q(vehicule_propose__marque__nom__icontains=q)|
                    Q(vehicule_propose__modele__icontains=q)|
                    Q(vehicule_propose__annee__icontains=q)
                )
            if statut:
                queryset = queryset.filter(statut=statut)
            
            if type_offre:
                queryset = queryset.filter(type_offre=type_offre)
                
            return queryset.order_by("-date_creation")
        
        else:
            queryset = Offre.objects.filter(client=self.request.user)
            q = self.request.GET.get("q")
            statut = self.request.GET.get("statut")
           
            if q:
                queryset = queryset.filter(
                    Q(client__nom_complet__icontains=q) |Q(client__email__icontains=q)|
                    Q(vehicule_propose__marque__nom__icontains=q)|
                    Q(vehicule_propose__modele__icontains=q)|
                    Q(vehicule_propose__annee__icontains=q)
                )
            if statut:
                queryset = queryset.filter(statut=statut)
                
                
            if type_offre:
                queryset = queryset.filter(type_offre=type_offre)
                            
          
            return queryset.order_by("-date_creation")
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["STATUTS_OFFRE"] = Offre.STATUTS_OFFRE
        context["TYPE_OFFRE"] = Offre.TYPE_OFFRE_CHOICES
        return context
        
class OffreDetailView(LoginRequiredMixin,UserPassesTestMixin ,DetailView):
    def test_func(self):
        return self.request.user.role in ['directeur', 'commercial', 'client']
    
    model = Offre
    context_object_name = "offre"
    
    
    def get_template_names(self):
        if self.request.user.is_superuser or self.request.user.role == "directeur":
            return['directeur_templates/directeur_offre_detail.html']
        
        elif self.request.user.is_staff or self.request.user.role == "commercial":
            return["commercial_templates/commercial_offre_detail.html"]
        
        return ["clients_templates/client_offre_detail.html"] 
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        if "upload_doc_form" not in context:
            context["upload_doc_form"] = DocumentsUploadForm()
        if self.request.user.role != "client":
            if "update_offre_form" not in context:
                context["update_offre_form"] = OffreFinancementForm(instance=self.object)
            if "update_offre_simple_form" not in context:
                context['update_offre_simple_form'] = OffreSimpleForm(instance=self.object)
            return context
        return context

class OffreUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Offre
    form_class = OffreFinancementForm
    
    
    def get_template_names(self):
        if self.request.user.is_superuser or self.request.user.role == "directeur":
            return ["directeur_templates/directeur_offre_detail.html"]
        return ["commercial_templates/commercial_offre_detail.html"]
    
    def test_func(self):
        return self.request.user.role in ['commercial', 'directeur']
    
    time.sleep(3)
    def form_valid(self, form):
        offre = form.save(commit=False)
        
        # Vérifier si l'offre était en brouillon et va être envoyée
        was_brouillon = offre.statut == 'brouillon'
        
        if was_brouillon:
            offre.statut = 'envoyee'
        
        offre.save()
        
        # ✉️ Envoyer un email au client si l'offre vient d'être envoyée
        if was_brouillon:
            try:
                context_email = {
                    'client': offre.client,
                    'offre_id': offre.id,
                    'vehicule': str(offre.vehicule_propose) if offre.vehicule_propose else "Véhicule sélectionné",
                    'montant_finance': offre.montant_finance,
                    'mensualite': offre.mensualite,
                    'duree_mois': offre.duree_mois,
                    'apport': offre.apport_demande,
                    'date_expiration': offre.date_expiration,
                    'lien_offre': self.request.build_absolute_uri(offre.get_absolute_url()),
                }
                html_message = render_to_string('emails/offres/offre_envoyee_client.html', context_email)
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject="📄 Une offre de financement Mis à jour - KOZ Services",
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[offre.client.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                messages.success(self.request, "Offre mise à jour et envoyée au client.")
            except Exception as e:
                logger.error(f"Offre mise à jour mais l'email n'a pas pu être envoyé.: {e}")
        response = render(self.request, "partials/offre/_offres_result.html",{
                                                        "success": True,
                                                        "title": "✅ Offre mis à jour ",
                                                        "message": f"Offre a été modifié pour {offre.client.nom_complet}. Un email a été envoyé.",
                                                        "reload_on_close":True
                                                    })
        response['HX-Trigger'] = "closeUpdateOffreModal"
        return response
    time.sleep(3)
    def form_invalid(self, form):
       return render(self.request, "partials/offre/_offre_simple_form_error.html", {"update_offre_form":form})
   
class OffreSimpleUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Offre
    form_class = OffreSimpleForm
    
    def test_func(self):
        return self.request.user.role in ['commercial', 'directeur'] 
   
    
    def get_template_names(self):
        if self.request.user.is_superuser or self.request.user.role == "directeur":
            return ["directeur_templates/directeur_offre_detail.html"]
        return ["commercial_templates/commercial_offre_detail.html"]
        
    def test_func(self):
        return self.request.user.role in ['commercial', 'directeur']
        
    time.sleep(3)
    def form_valid(self, form):
        offre = form.save(commit=False)
            
        # Vérifier si l'offre était en brouillon et va être envoyée
        was_brouillon = offre.statut == 'brouillon'
            
        if was_brouillon:
            offre.statut = 'envoyee'
            
            offre.save()
            
            # ✉️ Envoyer un email au client si l'offre vient d'être envoyée
            try:
                context_email = {
                        'client': offre.client,
                        'offre_id': offre.id,
                        'vehicule': str(offre.vehicule_propose) if offre.vehicule_propose else "Véhicule sélectionné",
                        'montant_propose': offre.montant_propose,
                        'date_expiration': offre.date_expiration,
                        'lien_offre': self.request.build_absolute_uri(offre.get_absolute_url()),
                    }
                html_message = render_to_string('emails/offres/offre_simple_MAJ_client.html', context_email)
                plain_message = strip_tags(html_message)
                    
                send_mail(
                        subject="📄  Offre  Mis à jour - KOZ Services",
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[offre.client.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                messages.success(self.request, "Offre mise à jour et envoyée au client.")
            except Exception as e:
                    logger.error(f"Offre mise à jour mais l'email n'a pas pu être envoyé.: {e}")
            response = render(self.request, "partials/offre/_offres_result.html",{
                                                            "success": True,
                                                            "title": "✅ Offre mis à jour ",
                                                            "message": f"Offre a été modifié pour {offre.client.nom_complet}. Un email a été envoyé.",
                                                            "reload_on_close":True
                                                        })
            response['HX-Trigger'] = "closeUpdateSimpleOffreModal"
            return response
    time.sleep(3)
    def form_invalid(self, form):
        return render(self.request, "partials/offre/_offre_simple_form_error.html", {"update_offre_simple_form":form})
             
class OffreDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Offre
    
    def get_success_url(self):
        return reverse_lazy("commercial_app:offre-list")
    
    def get_template_names(self):
        if self.request.user.is_superuser or self.request.user.role == "directeur":
            return["directeur_templates/directeur_offre.detail.html"]
        return ["commercial_templates/commercial_offre.detail.html"]
    
    def test_func(self):
        return self.request.user.role in ['commercial', 'directeur']


    def delete(self, request, *args, **kwargs):
        messages.success(request, "Offre supprimée.")
        return super().delete(request, *args, **kwargs)
    
######################################___________VENTE/GESTION_View__________________#########################################################

def changer_statut_vente(request, vente_id):
    if request.user.role not in ["directeur", "commercial"]:
        messages.warning(request, "Vous n'etes pas autorisé changer le status de cette vente")
        messages.warning(request, "Si toute fois nouvelle tentative votre compte sera bloqué")
        return redirect('home_app:home-page')
    
    time.sleep(1.5)
    vente = get_object_or_404(Vente, id=vente_id)
    
    if request.method == 'POST':
        nouveau_statut = request.POST.get('statut')
        with transaction.atomic():
            if nouveau_statut in dict(Vente.STATUT_VENTE).keys():
                ancien_statut = vente.statut
                vente.statut = nouveau_statut
                vente.save()
                
                # ============================================================
                # ✅ SI LA VENTE PASSE À "CONCLUE AVEC FINANCEMENT"
                # ============================================================
                statuts_avec_financement = [
                    'conclue_par_acceptation_offre_financement',
                    'conclue_sur_acceptation_demande_financement',
                ]
                
                if nouveau_statut in statuts_avec_financement:
                    # ✅ Vérifier si les échéances existent déjà
                    if not vente.echeances:
                        # ✅ Générer les échéances
                        if vente.offre:
                            echeances = generer_echeances_offre(vente.offre) 
                        elif vente.demande_financement:
                            echeances = generer_echeances_demande(vente.demande_financement)
                        else:
                            echeances = []
                        
                        if echeances:
                            vente.echeances = echeances
                             
                            vente.save()
                            
                            # ✅ Créer les PaiementFinancement
                            for echeance in echeances:
                                PaiementFinancement.objects.create(
                                    vente=vente,
                                    client=vente.client,
                                    montant=echeance['montant'],
                                    date_echeance=echeance['date'],
                                    statut='en_attente',
                                    reference=f"PAY-{vente.id}-{echeance['numero']}"
                                )
                        
                            response = render(request, "partials/vente/_vente_result.html",{
                                                                                            "success": True,
                                                                                            "title": "✅ vente mis à jour",
                                                                                            "message": f"✅ {len(echeances)} échéances créées pour le financement.",
                                                                                            "reload_on_close":True
                                                                                        })
                            response['HX-Trigger'] = "closeStatuGestionModal"
                            return response
                        else:
                            response = render(request, "partials/vente/_vente_result.html", {
                                "success": False,
                                "title": "❌ Erreur",
                                "message": "Impossible de générer les échéances : aucune offre ni demande associée à cette vente.",
                            })
                            response['HX-Trigger'] = "closeStatuGestionModal"
                            return response
                    else:
                        response = render(request, "partials/vente/_vente_result.html",{
                                                                                        "success": True,
                                                                                        "title": "✅ vente mis à jour",
                                                                                        "message":"les échéances crées depuis la validation du dossier",
                                                                                        "reload_on_close":True
                                                                                                            })
                        response['HX-Trigger'] = "closeStatuGestionModal"
                        return response
                
                # ============================================================
                # ❌ SI LA VENTE PASSE À "PERDUE"
                # ============================================================
                elif nouveau_statut.startswith('perdue'):
                    # ✅ Annuler les échéances non payées
                    PaiementFinancement.objects.filter(
                        vente=vente,
                        statut='en_attente',
                    ).update(statut='abandonne', date_paiement=timezone.now().date())
                    
                    response = render(request, "partials/vente/_vente_result.html",{
                                                                                "success": True,
                                                                                "title": "✅ vente mis à jour",
                                                                                "message": f" statut de vente mis à jour! Nouveau statut: {nouveau_statut}. Les échéances impayées sont abandonnées.",
                                                                                "reload_on_close":True
                                                                            })
                    response['HX-Trigger'] = "closeStatuGestionModal"
                    return response
                
                else:
                    response = render(request, "partials/vente/_vente_result.html",{
                                                                "success": True,
                                                                "title": "✅ vente mis à jour",
                                                                "message": f" statut de vente mis à jour! Nouveau statut: {nouveau_statut}.",
                                                                "reload_on_close":True
                                                            })
                    response['HX-Trigger'] = "closeStatuGestionModal"
                    return response
                    
            else:
                response = render(request, "partials/vente/_vente_result.html",{
                                                                        "success": False,
                                                                        "title": "❌échec de mise à jour",
                                                                        "message": "Statut invalide",
                                                                        "reload_on_close":True
                                                                    })
            response['HX-Trigger'] = "closeStatuGestionModal"
            return response
    
    return redirect('commercial_app:vente-detail', pk=vente.id)


@login_required
def marquer_paye(request, vente_id, numero_echeance):
    if request.user.role not in ["directeur", "commercial"]:
            messages.warning(request, "Vous n'etes pas autorisé changer le status de cette vente")
            messages.warning(request, "Si toute fois nouvelle tentative votre compte sera bloqué")
            return redirect('home_app:home-page')
    time.sleep(3)
    vente = get_object_or_404(Vente, id=vente_id)
    numero_echeance = int(numero_echeance)

    # ✅ Vérification des droits
    if request.user.role not in ['commercial', 'directeur']:
        response = render(request, "partials/vente/_vente_result.html", {
            "success": False,
            "title": "❌ Action non autorisée",
            "message": "Vous n'avez pas les droits pour effectuer cette action.",
        })
        response['HX-Trigger'] = "closePaiementModal"
        return response

    if request.method != 'POST':
        return redirect('commercial_app:vente-detail', vente.pk)

    # ✅ Validation de la date de paiement
    date_paiement_str = request.POST.get('date_paiement')
    try:
        date_paiement = (
            datetime.strptime(date_paiement_str, '%Y-%m-%d').date()
            if date_paiement_str else timezone.now().date()
        )
    except ValueError:
        response = render(request, "partials/vente/_vente_result.html", {
            "success": False,
            "title": "❌ Erreur",
            "message": "Date de paiement invalide.",
        })
        response['HX-Trigger'] = "closePaiementModal"
        return response

    with transaction.atomic():
        # ✅ Vérifier l'état actuel de l'échéance AVANT modification
        echeance_actuelle = next(
            (e for e in vente.echeances if e['numero'] == numero_echeance), None
        )

        if echeance_actuelle is None:
            response = render(request, "partials/vente/_vente_result.html", {
                "success": False,
                "title": "❌ Erreur",
                "message": f"Échéance #{numero_echeance} introuvable.",
            })
            response['HX-Trigger'] = "closePaiementModal"
            return response

        if echeance_actuelle['paye']:
            response = render(request, "partials/vente/_vente_result.html", {
                "success": False,
                "title": "ℹ️ Déjà payée",
                "message": f"L'échéance #{numero_echeance} est déjà marquée comme payée.",
            })
            response['HX-Trigger'] = "closePaiementModal"
            return response

        # ✅ Marquer l'échéance comme payée dans le JSON
        echeance_actuelle['paye'] = True
        echeance_actuelle['date_paiement'] = date_paiement.isoformat()

        # ✅ Apport déjà versé + toutes les échéances payées
        total_echeances_payees = sum(
            Decimal(str(e['montant'])) for e in vente.echeances if e['paye']
        )
        vente.montant_total_paye = vente.montant + total_echeances_payees
        vente.save()

        # ✅ Synchroniser le PaiementFinancement correspondant
        paiement = PaiementFinancement.objects.filter(
            vente=vente,
            reference=f"PAY-{vente.id}-{numero_echeance}"
        ).first()

        if paiement:
            paiement.statut = 'paye'
            paiement.date_paiement = date_paiement
            paiement.save()

    response = render(request, "partials/vente/_vente_result.html", {
        "success": True,
        "title": "✅ Paiement enregistré",
        "message": f"L'échéance #{numero_echeance} a été marquée comme payée.",
        "reload_on_close": True,
    })
    response['HX-Trigger'] = "closePaiementModal"
    return response


class venteSimpleCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    def test_func(self):
        return self.request.user.role in ['commercial', 'directeur']
    model = Vente
    form_class = VenteSimpleForm
    
    def form_valid(self, form):
        time.sleep(3)
        vente = form.save(commit=False)
        vente.montant_total_paye = form.cleaned_data.get("montant")
        vente.statut = "gestion_de_statut"
        vente.save()
        
        response = render(self.request, "partials/vente/_vente_result.html", {'success': True,
                                                                               'title': '✅ Enregisté',
                                                                               'message': 'Vente enregisté avec succès',
                                                                               'reload_on_close': True,
                                                                              })
        response['HX-Trigger'] = "closeVenteModal"
        return response
    
    def form_invalid(self, form):
        response = render(self.request, "partials/vente/_vente_result.html", {'success': False,
                                                                                       'title': '❌Echec',
                                                                                       'message': "La vente n'a pas été enrégistré",
                                                                                       'reload_on_close': False,
                                                                                      })
        response['HX-Trigger'] = "closeVenteModal"
        return response
            
class VenteListView(LoginRequiredMixin,UserPassesTestMixin ,ListView):
    def test_func(self):
        return self.request.user.role in ['commercial', 'directeur']
                    
    model = Vente
    context_object_name = "ventes"
    paginate_by = 20

    def get_template_names(self):
        is_htmx = self.request.headers.get('HX-Request') == 'true'
        if self.request.user.is_superuser or self.request.user.role  == "directeur":
            return ["partials/vente/partials_vente_list.html" if is_htmx else "directeur_templates/directeur_vente_list.html"]
        return ["partials/vente/partials_vente_list.html" if is_htmx else "commercial_templates/commercial_vente_list.html"]
       
        
    def get_queryset(self):
        # 1. Base queryset selon le rôle
        if self.request.user.is_superuser or self.request.user.role == "directeur":
            queryset = Vente.objects.all()
            
        elif self.request.user.is_staff or self.request.user.role == "commercial":
            queryset = Vente.objects.all()
        else:
            return Vente.objects.none()

        # 2. Optimisation
        queryset = queryset.select_related('client', 'demande_financement').order_by('-date_vente')

        # 3. Filtres communs
        statut = self.request.GET.get('statut')
        type_vente = self.request.GET.get('type_vente')
        client_name = self.request.GET.get('client')

        if statut:
            queryset = queryset.filter(statut=statut)
        if type_vente:
            queryset = queryset.filter(type_vente=type_vente)
        if client_name:
            queryset = queryset.filter(client__nom_complet__icontains=client_name)

        return queryset
                

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statut_choices'] = Vente.STATUT_VENTE
        if "simple_vente_form" not in context:
            context["simple_vente_form"] = VenteSimpleForm()
        return context

class VenteDetailView(LoginRequiredMixin,UserPassesTestMixin ,DetailView):
    def test_func(self):
        return self.request.user.role in ['commercial', 'directeur']
    model = Vente
    template_name = "commercial_templates/vente_detail.html"
    context_object_name = "vente"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["STATUT_VENTE"] = Vente.STATUT_VENTE
        return context

############################################# GESTION_MAINTENANCE_VIEW ##########################################################################

@login_required
def confirmer_maintenance(request, maintenance_id):
    maintenance = get_object_or_404(Maintenance, id=maintenance_id, client=request.user)
    
    if maintenance.statut != 'planifiee':
        response = render(request, "partials/maintenance/_maintenance_result.html",{'success': False,
                                                                                               'title': '❌échec',
                                                                                               'message': 'Cette maintenance ne peut pas être confirmée.',
                                                                                               'reload_on_close': False,
                                                                                              })
        response['HX-Trigger'] = "closeGestMaintenanceModal"
        return response
    
    maintenance.statut = 'confirmee'
    maintenance.save()
    
    # ✉️ Email à tous les commerciaux
    commerciaux = kozUser.objects.filter(role='commercial')
    if commerciaux.exists():
        try:
            for commercial in commerciaux:
                if not commercial.email:
                    continue
                context_email = {
                    'client': maintenance.client,
                    'commercial': commercial,
                    'maintenance': maintenance,
                    'lien_maintenance': request.build_absolute_uri(maintenance.get_absolute_url()),
                }
                html_message = render_to_string('emails/maintenance/maintenance_confirmee_commercial.html', context_email)
                plain_message = strip_tags(html_message)
                send_mail(
                    subject="✅ Un client a confirmé sa maintenance - KOZ Services",
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[commercial.email],
                    html_message=html_message,
                    fail_silently=False,
                )
        except Exception as e:
            logger.error(f"Erreur envoi email: {e}")
    
    
    response = render(request, "partials/maintenance/_maintenance_result.html",{'success': True,
                                                                                   'title': '✅ Succès',
                                                                                   'message': 'Votre maintenance a été confirmée. Un email a été envoyé à votre commercial.',
                                                                                   'reload_on_close': True,
                                                                                  })
    response["HX-Trigger"] = "closeGestMaintenanceModal"
    return response

    
@login_required
def refuser_maintenance(request, maintenance_id):
    maintenance = get_object_or_404(Maintenance, id=maintenance_id, client=request.user)
    
    if maintenance.statut != 'planifiee':
        response = render(request, "partials/maintenance/_maintenance_result.html",{'success': False,
                                                                                                      'title': '❌échec',
                                                                                                      'message': 'Cette maintenance ne peut pas être annulée.',
                                                                                                      'reload_on_close': False,
                                                                                                     })
        response['HX-Trigger'] = "closeGestMaintenanceModal"
        return response
    
    maintenance.statut = 'annulee'
    maintenance.save()
    
    # ✉️ Email à tous les commerciaux
    commerciaux = kozUser.objects.filter(role='commercial')
    if commerciaux.exists():
        try:
            for commercial in commerciaux:
                if not commercial.email:
                    continue
                context_email = {
                    'client': maintenance.client,
                    'commercial': commercial,
                    'maintenance': maintenance,
                    'lien_maintenance': request.build_absolute_uri(maintenance.get_absolute_url()),
                }
                html_message = render_to_string('emails/maintenance/maintenance_annulee_commercial.html', context_email)
                plain_message = strip_tags(html_message)
                send_mail(
                    subject="❌ Un client a annulé sa maintenance - KOZ Services",
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[commercial.email],
                    html_message=html_message,
                    fail_silently=False,
                )
        except Exception as e:
            logger.error(f"Erreur envoi email: {e}")
    
    
    response = render(request, "partials/maintenance/_maintenance_result.html",{'success': True,
                                                                                       'title': '✅ Succès',
                                                                                       'message': 'Votre maintenance a été annulée. Votre commercial a été notifié.',
                                                                                       'reload_on_close': True,
                                                                                      })
    response["HX-Trigger"] = "closeGestMaintenanceModal"
    return response


def changer_statut_maintenance(request, maintenance_id, nouveau_statut):
    maintenance = get_object_or_404(Maintenance, id=maintenance_id)
    
    # Vérifier que l'utilisateur est commercial ou directeur
    if request.user.role not in ['commercial', 'directeur']:
        messages.error(request, "Action non autorisée.")
        return redirect('commercial_app:maintenance-detail', pk=maintenance.id)
    
    statuts_valides = ['en_cours', 'effectuee', 'annulee']
    if nouveau_statut not in statuts_valides:
        messages.error(request, "Statut invalide.")
        return redirect('commercial_app:maintenance-detail', pk=maintenance.id)
    
    maintenance.statut = nouveau_statut
    if nouveau_statut == 'effectuee':
        maintenance.date_derniere = timezone.now().date()
        maintenance.kilometrage_dernier = maintenance.kilometrage_actuel
    maintenance.save()
    
    # ✉️ Email au client
    try:
        context_email = {
            'client': maintenance.client,
            'maintenance': maintenance,
            'nouveau_statut': maintenance.get_statut_display(),
            'lien_maintenance': request.build_absolute_uri(maintenance.get_absolute_url()),
        }
        
        if nouveau_statut == 'en_cours':
            template = 'emails/maintenance/maintenance_en_cours_client.html'
            sujet = "🔄 Votre maintenance est en cours - KOZ Services"
        elif nouveau_statut == 'effectuee':
            template = 'emails/maintenance/maintenance_effectuee_client.html'
            sujet = "✅ Votre maintenance est terminée - KOZ Services"
        else:
            template = 'emails/maintenance/maintenance_annulee_client.html'
            sujet = "❌ Votre maintenance a été annulée - KOZ Services"
        
        html_message = render_to_string(template, context_email)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=sujet,
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[maintenance.client.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Erreur envoi email: {e}")
    
    response = render(request, "partials/maintenance/_maintenance_result.html",{'success': True,
                                                                            'title': '✅ Succès',
                                                                            'message': f"Maintenance passée en '{maintenance.get_statut_display()}'. Le client a été notifié.",
                                                                            'reload_on_close': True,
                                                                                      })
    response["HX-Trigger"] = "closeGestMaintenanceModal"
    return response


#######################################__________________MAINTENANCE_VIEW_______________##################################################
class MaintenanceListView(LoginRequiredMixin, ListView):
    model = Maintenance
    context_object_name = "maintenances"
    
    
    def get_template_names(self):
        is_htmx = self.request.headers.get('HX-Request') == 'true'
        if self.request.user.role == "directeur" or self.request.user.is_superuser:
            return ["partials/maintenance/partials_maintenance_list.html" if is_htmx else "directeur_templates/directeur_maintenance_list.html"]
        
        if self.request.user.role == "commercial" or self.request.user.is_staff: 
            return ["partials/maintenance/partials_maintenance_list.html" if is_htmx else "commercial_templates/commercial_maintenance_list.html"]
        
        return["partials/maintenance/partials_maintenance_list.html" if is_htmx else 'clients_templates/client_maintenance_list.html']
        
    
    def get_queryset(self):
        #Si commercial : Voir maintenances des ses clients
        if self.request.user.role == "commercial" or (self.request.user.is_staff and not self.request.user.is_superuser):
            queryset = Maintenance.objects.filter(client__assigned_commercial=self.request.user).select_related("client")
            q = self.request.GET.get("q")
            type_maintenance = self.request.GET.get("type_maintenance")
            priorite = self.request.GET.get("priorite")
            origine = self.request.GET.get("origine")
            statut = self.request.GET.get("statut")
            effectue_par = self.request.GET.get("effectue_par")
            
            if q:
                queryset = queryset.filter(
                    Q(client__nom_complet__icontains=q) |
                    Q(marque__icontains=q) |
                    Q(modele__icontains=q)|
                    Q(vehicul__marque__nom__icontains=q)|
                    Q(vehicul__modele__icontains=q)|
                    Q(vehicul__annee__icontains=q)|
                    Q(immatriculation__icontains=q)|
                    Q(notes_client__icontains=q)|
                    Q(notes_technicien__icontains=q)|
                    Q(effectue_par__nom_complet__icontains=q)
                )
            
            if type_maintenance:
                queryset = queryset.filter(type_maintenance=type_maintenance)
            
            if priorite:
                queryset = queryset.filter(priorite=priorite)
            
            if origine:
                queryset = queryset.filter(origine=origine)
            
            if statut:
                queryset = queryset.filter(statut=statut)
            
            if effectue_par:
                queryset = queryset.filter(effectue_par=effectue_par)

            return queryset.order_by
            
        
        #Si client: Voir ses maintenance 
        elif self.request.user.role == "client":
            queryset = Maintenance.objects.filter(client=self.request.user)
            q = self.request.GET.get("q")
            type_maintenance = self.request.GET.get("type_maintenance")
            priorite = self.request.GET.get("priorite")
            origine = self.request.GET.get("origine")
            statut = self.request.GET.get("statut")
            effectue_par = self.request.GET.get("effectue_par")
            
            if q:
                queryset = queryset.filter(
                    Q(client__nom_complet__icontains=q) |
                    Q(marque__icontains=q) |
                    Q(modele__icontains=q)|
                    Q(vehicul__marque__nom__icontains=q)|
                    Q(vehicul__modele__icontains=q)|
                    Q(vehicul__annee__icontains=q)|
                    Q(immatriculation__icontains=q)|
                    Q(notes_client__icontains=q)|
                    Q(notes_technicien__icontains=q)|
                    Q(effectue_par__nom_complet__icontains=q)
                )
            
            if type_maintenance:
                queryset = queryset.filter(type_maintenance=type_maintenance)
            
            if priorite:
                queryset = queryset.filter(priorite=priorite)
            
            if origine:
                queryset = queryset.filter(origine=origine)
            
            if statut:
                queryset = queryset.filter(statut=statut)
            
            if effectue_par:
                queryset = queryset.filter(effectue_par=effectue_par)

            return queryset.order_by("-date_creation")
            

        else:
            queryset = Maintenance.objects.all()
            q = self.request.GET.get("q")
            type_maintenance = self.request.GET.get("type_maintenance")
            priorite = self.request.GET.get("priorite")
            origine = self.request.GET.get("origine")
            statut = self.request.GET.get("statut")
            effectue_par = self.request.GET.get("effectue_par")
            
            if q:
                queryset = queryset.filter(
                    Q(client__nom_complet__icontains=q) |
                    Q(marque__icontains=q) |
                    Q(modele__icontains=q)|
                    Q(vehicul__marque__nom__icontains=q)|
                    Q(vehicul__modele__icontains=q)|
                    Q(vehicul__annee__icontains=q)|
                    Q(immatriculation__icontains=q)|
                    Q(notes_client__icontains=q)|
                    Q(notes_technicien__icontains=q)|
                    Q(effectue_par__nom_complet__icontains=q)
                )
            
            if type_maintenance:
                queryset = queryset.filter(type_maintenance=type_maintenance)
            
            if priorite:
                queryset = queryset.filter(priorite=priorite)
            
            if origine:
                queryset = queryset.filter(origine=origine)
            
            if statut:
                queryset = queryset.filter(statut=statut)
            
            if effectue_par:
                queryset = queryset.filter(effectue_par=effectue_par)

            return queryset.order_by("-date_creation")
            
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context["maintenance_form"] = MaintenanceForm()
        context["TYPE_CHOICES"] = Maintenance.TYPE_CHOICES
        context["priorite_choices"] = Maintenance.PRIORITE_CHOICES
        context["origine_choices"] = Maintenance.ORIGINE_CHOICES
        context["STATUT_CHOICES"] = Maintenance.STATUT_CHOICES
        return context
    
class MaintenanceCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = "commercial_templates/maintenance_list.html"

    def test_func(self):
        return self.request.user.role in ['commercial', 'directeur']

    def form_valid(self, form):
        # ⏱️ Simule un traitement (à supprimer en prod)
        time.sleep(1.5)
        
        # ✅ Sauvegarde du formulaire
        maintenance = form.save()
        
        # ==========================================
        # 📧 ENVOI DE L'EMAIL AU CLIENT
        # ==========================================
        client = maintenance.client  # Assure-toi que Maintenance a un FK vers Client
        
        if client and client.email:
            try:
                # Contexte pour le template
                context_email = {
                    'client': client,
                    'vehicule': maintenance.vehicul if hasattr(maintenance, 'vehicul') else "Véhicule",
                    'date_prevue': maintenance.date_prevue if hasattr(maintenance, 'date_prevue') else None,
                    'type_maintenance': maintenance.type_maintenance if hasattr(maintenance, 'type_maintenance') else "Révision",
                    'notes_technicien': maintenance.notes_technicien if hasattr(maintenance, 'notes_technicien') else "",
                    'commercial': self.request.user,
                    'lien_suivi': self.request.build_absolute_uri(maintenance.get_absolute_url()),
                }
                
                # Rendu du template HTML
                html_message = render_to_string('emails/maintenance/maintenance_creation_client.html',context_email)
                plain_message = strip_tags(html_message)
                
                # Envoi de l'email
                send_mail(
                    subject=f"🛠️ Confirmation de maintenance - {context_email['vehicule']}",
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[client.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
            except Exception as e:
                # On log l'erreur mais on continue (pas bloquant pour la réponse HTMX)
                logger.error(f"Erreur envoi email maintenance client: {e}")
        
        # ==========================================
        # ✅ RÉPONSE HTMX
        # ==========================================
        response = render(self.request, "partials/maintenance/_maintenance_result.html", {
            'success': True,
            'title': '✅ Créee',
            'message': 'Maintenance créee avec succès',
            'reload_on_close': True,
        })
        response["HX-Trigger"] = "closeMaintenanceModal"
        return response
    
    def form_invalid(self, form):
        return render(self.request, 'partials/_maintenance_form_errors.html', {"maintenance_form": form})
        
    
class MaintenanceDetailView(LoginRequiredMixin, DetailView):
    model = Maintenance
    context_object_name = "maintenance"
    
    def get_template_names(self):
        is_htmx = self.request.headers.get('HX-Request') == 'true'
        if self.request.user.role == "directeur" or self.request.user.is_superuser:
            return ["partials/maintenance/partials_maintenance_detail.html" if is_htmx else "directeur_templates/directeur_maintenance_detail.html"]
        
        if self.request.user.role == "commercial" or self.request.user.is_staff: 
            return ["partials/maintenance/partials_maintenance_detail.html" if is_htmx else "commercial_templates/commercial_maintenance_detail.html"]
        
        return["partials/maintenance/partials_maintenance_detail.html" if is_htmx else 'clients_templates/client_maintenance_detail.html']

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role in ['commercial', 'directeur']:
            if  "update_maintenance_form" not in context:
                context["update_maintenance_form"] = MaintenanceForm(instance=self.object)
            return context
        
        return context

class MaintenanceUpdateView(LoginRequiredMixin, UserPassesTestMixin,UpdateView):
    model= Maintenance
    template_name = "commercial_templates/maintenance_detail.html"
    form_class = MaintenanceForm

    def test_func(self):
        return self.request.user.role in ['commercial', 'directeur']
    
    def form_valid(self, form):
        time.sleep(1.5)
        maintenance = form.save()
                
                # ==========================================
                # 📧 ENVOI DE L'EMAIL AU CLIENT
                # ==========================================
        client = maintenance.client  # Assure-toi que Maintenance a un FK vers Client
                
        if client and client.email:
            try:
                        # Contexte pour le template
                context_email = {
                            'client': client,
                            'vehicule': maintenance.vehicul if hasattr(maintenance, 'vehicul') else "Véhicule",
                            'date_prevue': maintenance.date_prevue if hasattr(maintenance, 'date_prevue') else None,
                            'type_maintenance': maintenance.type_maintenance if hasattr(maintenance, 'type_maintenance') else "Révision",
                            'notes_technicien': maintenance.notes_technicien if hasattr(maintenance, 'notes_technicien') else "",
                            'commercial': self.request.user,
                            'lien_suivi': self.request.build_absolute_uri(maintenance.get_absolute_url()),
                        }
                        
                        # Rendu du template HTML
                html_message = render_to_string('emails/maintenance/maintenance_creation_client.html',context_email)
                plain_message = strip_tags(html_message)
                        
                        # Envoi de l'email
                send_mail(
                            subject=f"🛠️ Confirmation de maintenance - {context_email['vehicule']}",
                            message=plain_message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[client.email],
                            html_message=html_message,
                            fail_silently=False,
                        )
                        
            except Exception as e:          
                # On log l'erreur mais on continue (pas bloquant pour la réponse HTMX)
                logger.error(f"Erreur envoi email maintenance client: {e}")
        
        response = render(self.request, "partials/maintenance/_maintenance_result.html",{'success': True,
                                                                                      'title': '✅ Modifiée',
                                                                                      'message': 'Maintenance modfifié avec succès',
                                                                                      'reload_on_close': True,
                                                                                     })
        response["HX-Trigger"] = "closeMaintenanceModal"
        return response
    
    def form_invalid(self, form):
        return render(self.request, 'partials/_maintenance_form_errors.html',{"update_maintenance_form":form})
      
class MaintenanceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Maintenance
    template_name = "commercial_templates/maintenance_detail.html"
    success_url = reverse_lazy("commercial_app:maintenance-list")

    def test_func(self):
        return self.request.user.role in ['commercial', 'directeur']

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Maintenance supprimée.")
        return super().delete(request, *args, **kwargs)

class CommercialRendezVousListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = RendezVous
    template_name = 'commercial_templates/rendez_vous_list.html'
    context_object_name = 'rendez_vous'
    paginate_by = 10

    def test_func(self):
        return self.request.user.role == 'commercial' or self.request.user.is_staff

    def get_queryset(self):
        queryset = RendezVous.objects.all().order_by('date_rendez_vous')
        
        statut = self.request.GET.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statut_choices'] = RendezVous.STATUT_CHOICES
        context['statistiques'] = {
            'en_attente': RendezVous.objects.filter(statut='en_attente').count(),
            'confirme': RendezVous.objects.filter(statut='confirme').count(),
            'annule': RendezVous.objects.filter(statut='annule').count(),
            'termine': RendezVous.objects.filter(statut='termine').count(),
        }
        return context


@login_required
def confirmer_rdv(request, rdv_id):
    rdv = get_object_or_404(RendezVous, id=rdv_id)
    rdv.statut = 'confirme'
    rdv.save()
    messages.success(request, f"✅ Rendez-vous du {rdv.date_rendez_vous.strftime('%d/%m/%Y à %H:%M')} confirmé !")
    return redirect('commercial_app:rendez-vous-list')


@login_required
def annuler_rdv(request, rdv_id):
    rdv = get_object_or_404(RendezVous, id=rdv_id)
    rdv.statut = 'annule'
    rdv.save()
    messages.warning(request, f"❌ Rendez-vous du {rdv.date_rendez_vous.strftime('%d/%m/%Y à %H:%M')} annulé.")
    return redirect('commercial_app:rendez-vous-list')


@login_required
def terminer_rdv(request, rdv_id):
    rdv = get_object_or_404(RendezVous, id=rdv_id)
    rdv.statut = 'termine'
    rdv.save()
    messages.success(request, f"✅ Rendez-vous du {rdv.date_rendez_vous.strftime('%d/%m/%Y à %H:%M')} terminé !")
    return redirect('commercial_app:rendez-vous-list')