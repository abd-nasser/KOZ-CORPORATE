from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.contrib import messages
from django.views.generic import CreateView, TemplateView, DetailView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


from auth_app.forms import  ChangePasswordForm
from commercial_app.forms import OffreFinancementForm, OffreSimpleForm
from .models import Documents
from auth_app.models import kozUser
from leads_app.models import demande_financement


class ClientDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
   def test_func(self):
       return self.request.user.role == "client"
   template_name = "clients_templates/client.html"
   
   def get_context_data(self, **kwargs):
      context =  super().get_context_data(**kwargs)
      
      
      context["client"] = self.request.user
      context["commercial"] = self.request.user.assigned_commercial
      context["commerciaux"] =  kozUser.objects.filter(role="commercial", est_actif=True)
      if 'change_pass_form' not in context:
         context["change_pass_form"] = ChangePasswordForm()
      return context

class clientListView(LoginRequiredMixin, ListView):
   model = kozUser
   template_name = "clients_templates/client_list.html"
   context_object_name = "clients"
   def get_queryset(self):
      return kozUser.objects.filter(role="client")

# commercial_app/views.py (ou client_app/views.py)

class ClientDetailView(LoginRequiredMixin, DetailView):
    model = kozUser
    template_name = "clients_templates/client_detail.html"
    context_object_name = "client"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Ajoute le formulaire d'offre simple dans le contexte
        if "offre_simple_form" not in context:
            context["offre_simple_form"] = OffreSimpleForm()
            
        if "offre_financement_form" not in context:
            context["offre_financement_form"] = OffreFinancementForm()
        
        # Ajoute aussi d'autres formulaires si nécessaire (ex: change_password, etc.)
        if "change_pass_form" not in context:
            context["change_pass_form"] = ChangePasswordForm(user=self.request.user)
        
        return context

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from home_app.models import RendezVous
from commercial_app.forms import RdvForm, ClientRdvForm  # Ou ton formulaire de RDV



class MesRendezVousListView(LoginRequiredMixin, ListView):
    """
    CBV 1 : Affichage de la liste des RDV et des métriques
    """
    model = RendezVous
    template_name = 'clients_templates/client_rdv_list.html'
    context_object_name = 'rendez_vous_list'

    def get_queryset(self):
        return RendezVous.objects.filter(client=self.request.user).order_by('-date_rendez_vous')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        
        context['rdv_form'] = ClientRdvForm(initial={'client': self.request.user})
        context['stats'] = {
            'total': queryset.count(),
            'a_venir': queryset.filter(statut__in=['en_attente', 'confirme']).count(),
            'termines': queryset.filter(statut='termine').count(),
        }
        return context


class ClientRdvCreateView(LoginRequiredMixin, CreateView):
    """
    CBV 2 : Traitement exclusif de la création de RDV
    """
    model = RendezVous
    form_class = ClientRdvForm
    success_url = reverse_lazy('client_app:mes-rendez-vous')

    def form_valid(self, form):
        client = self.request.user
        rdv = form.save(commit=False)
        
        # Remplissage automatique
        rdv.client = client
        rdv.email = client.email
        rdv.telephone = getattr(client, 'telephone', '')
        rdv.statut = 'en_attente'

        # Auto-remplissage nom/prénom pour éviter les contraintes BDD NOT NULL
        parts = (getattr(client, 'nom_complet', '')).strip().split(maxsplit=1)
        rdv.nom = parts[0] if parts else client.nom_complet
        rdv.prenom =  parts[1] if len(parts) > 1 else ''

        rdv.save()  # Un seul save() suffit
        messages.success(self.request, "Votre demande de rendez-vous a bien été transmise !")
        return super().form_valid(form)

    def form_invalid(self, form):
        # Affiche l'erreur exacte dans les messages flash pour debugger rapidement
        messages.error(self.request, f"Erreur de validation : {form.errors.as_text()}")
        return redirect('client_app:mes-rendez-vous')