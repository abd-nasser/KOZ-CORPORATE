from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages

from client_app.models import Maintenance
from vehicul_app.models import Vehicul
from .models import TypesServices, Services
from .forms import ReservationMaintenanceForm, TypesServicesForm, ServicesForm
from .models import Services, ServiceAvis
from .models import Services, ServiceImages
from .forms import ServiceImagesForm, ServiceAvisForm, ServiceAvisApprobationForm
from chat_app.models import Message
from auth_app.models import kozUser

from django.core.mail import send_mail
from koz_flow.tasks import send_email_task, send_receipt_email_task
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from leads_app.utils import generer_echeances_offre, generer_echeances_demande, calculer_mensualite
from utils.pdf import render_to_pdf
from django.conf import settings


import logging



logger = logging.getLogger(__name__)
# ============================================================
# TYPES DE SERVICES
# ============================================================
class TypesServicesListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = TypesServices
    template_name = "services_templates/type_services_list.html"
    context_object_name = "types_services_list"
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"


class TypesServicesCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = TypesServices
    form_class = TypesServicesForm
    template_name = "services_templates/directeur.html"
    success_url = reverse_lazy('directeur_app:directeur-view')
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"✅ Type de service '{self.object.nom}' créé avec succès !")
        return response
    
    def form_invalid(self, form):
        context = self.get_context_data()
        context['types_services_form'] = form
        context['open_types_services_modal'] = True
        return self.render_to_response(context)


# ============================================================
# SERVICES
# ============================================================
class ERP_ServicesCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Services
    form_class = ServicesForm
    template_name = "services_templates/directeur.html"
    success_url = reverse_lazy('directeur_app:directeur-view')
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"✅ Service '{self.object.nom}' créé avec succès !")
        return response
    
    def form_invalid(self, form):
        context = self.get_context_data()
        context['services_form'] = form
        context['open_services_modal'] = True
        return self.render_to_response(context)
    
    
class ERP_ServicesListView(LoginRequiredMixin, ListView):
    model = Services
    context_object_name = "services_list"
    template_name = "directeur_templates/directeur_services_list.html"
    
    
class ERP_ServiceDetailView(LoginRequiredMixin, DetailView):
    model = Services
    context_object_name = 'service'
    template_name = 'directeur_templates/directeur_service_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["avis"] = ServiceAvis.objects.all()
        # Formulaire pour le directeur
        if self.request.user.is_superuser or self.request.user.role == 'directeur':
            if 'service_images_form' not in context:
                context['service_images_form'] = ServiceImagesForm()
            if 'avis_approuve_form' not in context:
                context["avis_approuve_form"] = ServiceAvisApprobationForm()
            if 'update_service_form' not in context:
                context["update_service_form"] = ServicesForm(instance=self.object)
        return context



class ERP_ServiceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Services
    form_class = ServicesForm
    template_name = 'directeur_templates/directeur_service_detail.html'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == 'directeur'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"✅ Service '{self.object.nom}' mis à jour avec succès !")
        return response

    def form_invalid(self, form):
        context = self.get_context_data()
        context['update_service_form'] = form
        context['open_update_service_modal'] = True
        return self.render_to_response(context)

    def get_success_url(self):
        return reverse_lazy('directeur_app:directeur-view')


class ERP_ServiceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Services
    template_name = 'directeur_templates/directeur.html'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == 'directeur'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Service supprimé.")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('directeur_app:directeur-view')
    
class ERP_ServiceAvisApprobationView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ServiceAvis
    form_class = ServiceAvisApprobationForm
    template_name = "directeur_templates/directeur_service_detail.html"
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    
    def form_valid(self, form):
        response = super().form_valid(form)
        if self.object.est_approuve:
            messages.success(self.request, f"✅ Avis approuvé pour le service '{self.object.service.nom}'")
        else:
            messages.warning(self.request, f"⚠️ Avis désapprouvé pour le service '{self.object.service.nom}'")
        return response
    
    def get_success_url(self):
        return reverse_lazy('directeur_app:directeur-view')
class ERP_ServiceImagesCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ServiceImages
    form_class = ServiceImagesForm
    template_name = "directeur_templates/directeur.html"
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    
    def dispatch(self, request, *args, **kwargs):
        self.service = get_object_or_404(Services, pk=self.kwargs['service_pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = self.service
        context['open_service_images_modal'] = True
        return context
    
    def form_valid(self, form):
        form.instance.service = self.service
        response = super().form_valid(form)
        messages.success(self.request, f"✅ Image ajoutée au service '{self.service.nom}'")
        return response
    
    def get_success_url(self):
        return reverse_lazy('directeur_app:directeur-view')




class SITE_ServicesListView(ListView):
    model = Services
    context_object_name = "services"
    template_name = "services_templates/services_list.html"
    
class SITE_ServiceDetailView(DetailView):
    model = Services
    context_object_name = 'service'
    template_name = 'services_templates/service_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["avis_approuve"] = ServiceAvis.objects.filter(est_approuve = True, service=self.object)
        # Formulaire d'avis pour les clients
        if 'service_avis_form' not in context:
            context['service_avis_form'] = ServiceAvisForm()
        
        if 'reserver_service_form' not in context:
            context['reserver_service_form']=ReservationMaintenanceForm(client=self.request.user)
        return context


class SITE_ServiceAvisCreateView(LoginRequiredMixin, CreateView):
    model = ServiceAvis
    form_class = ServiceAvisForm
    template_name = "services_templates/service_detail.html"
    
    def dispatch(self, request, *args, **kwargs):
        self.service = get_object_or_404(Services, pk=self.kwargs['service_pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = self.service
        context['open_avis_modal'] = True
        return context
    
    def form_valid(self, form):
        form.instance.service = self.service
        form.instance.client = self.request.user
        # Par défaut, les avis sont en attente d'approbation
        form.instance.est_approuve = False
        response = super().form_valid(form)
        messages.success(self.request, "✅ Merci pour votre avis ! Il sera visible après validation.")
        return response
    
    def get_success_url(self):
        return reverse_lazy('services_app:service-detail-public', kwargs={'pk': self.service.pk})

@login_required
def reserver_service(request, service_id):
    service = get_object_or_404(Services, pk=service_id)

    if request.method != 'POST':
        return redirect("services_app:service-detail-public", service.pk)
    
        
    form = ReservationMaintenanceForm(request.POST, client=request.user)
    if not form.is_valid():
         return render(request, "partials/services/_reservation_form_errors.html", {"reserver_service_form": form})
        
    try:
        with transaction.atomic():
            maintenance = form.save(commit=False)
            maintenance.client = request.user
            maintenance.service = service
            maintenance.type_maintenance = service.type_maintenance_associe
            maintenance.origine = form.cleaned_data.get("origine")
            maintenance.vehicul = form.cleaned_data.get("vehicul")
            maintenance.marque = form.cleaned_data.get('marque')
            maintenance.modele = form.cleaned_data.get('modele')
            maintenance.annee = form.cleaned_data.get('annee')
            maintenance.immatriculation = form.cleaned_data.get('immatriculation')
            maintenance.save()

            commerciaux = kozUser.objects.filter(role='commercial', is_active=True)
            context_email = {
                'client': request.user,
                'maintenance': maintenance,
                "vehicule": maintenance.vehicul if maintenance.vehicul else f'{maintenance.marque}-{maintenance.modele}',
                'date_prevue': maintenance.date_prevue,
                'notes_client': maintenance.notes_client if maintenance.notes_client else "",
                'type_maintenance': maintenance.type_maintenance if maintenance.type_maintenance else "Révision",
                'lien_detail': request.build_absolute_uri(maintenance.get_absolute_url()),
                'date_creation': timezone.now(),
            }
            html_message = render_to_string('emails/maintenance/maintenance_creation_client_commercial.html', context_email)
            plain_message = strip_tags(html_message)

            recipients = [com.email for com in commerciaux if com.email]

            if recipients:
                transaction.on_commit(
                    lambda: send_email_task.delay(
                        subject=f"🛠️ Nouvelle maintenance demandée par {request.user.nom_complet}",
                        plain_message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=recipients,
                        html_message=html_message,
                    )
                )
                logger.info(f"Email maintenance envoyé à {len(recipients)} commerciaux")
            else:
                logger.warning("Aucun commercial actif trouvé pour l'envoi de l'email")

            response = render(request, "partials/maintenance/_maintenance_result.html", {
                'success': True,
                'title': '✅ Demande envoyée',
                'message': 'Votre demande de maintenance a bien été enregistrée.',
                'reload_on_close': True,
            })
            response["HX-Trigger"] = "CloseReservationModal"
            return response

    except Exception as e:
        logger.error(f"Erreur {e} -- sur la création de la maintenance")
        response = render(request, "partials/maintenance/_maintenance_result.html", {
            'success': False,
            'title': '❌ Erreur',
            'message': "Une erreur est survenue. Merci de réessayer.",
            'reload_on_close':True
        })
        return response
                        
           
@login_required
def contacter_service(request, service_id):
    service = get_object_or_404(Services, pk=service_id)
    
    message_content = f"""Bonjour,

    Je suis intéressé par le service suivant :
    🔧 {service.nom}
    📋 {service.description_courte}

    Pouvez-vous me donner plus d'informations ou me proposer un rendez-vous ?

    Cordialement,
    {request.user.nom_complet}"""

    commerciaux = kozUser.objects.filter(role='commercial')
    for commercial in commerciaux:
           Message.objects.create(
               client=request.user,
               commercial=commercial,
               contenu=message_content,
               est_client=True
       )
       
    
    messages.success(request, f"✅ Votre demande pour {service.nom} a été envoyée.")
    return redirect('chat_app:chat-view')
    