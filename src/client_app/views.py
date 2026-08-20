from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.contrib import messages
from django.views.generic import TemplateView, DetailView, ListView, UpdateView, DeleteView
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


