from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from .models import TypesServices, Services
from .forms import TypesServicesForm, ServicesForm
from .models import Services, ServiceAvis
from .models import Services, ServiceImages
from .forms import ServiceImagesForm, ServiceAvisForm, ServiceAvisApprobationForm
from chat_app.models import Message
from auth_app.models import kozUser



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
    context_object_name = "services_list"
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