from django.shortcuts import render
from django.views.generic import ListView, DeleteView, DetailView, CreateView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin #pour la connection requise et permission selon le role


from auth_app.forms import UserRegisterForm, ChangePasswordForm
from home_app.models import RendezVous
from vehicul_app.forms import MarqueForm, VehiculForm, TypeVehiculeForm
from products_app.forms import CategorieProductsForm, ProductsForm, UniteProduitForm, MarqueProduitForm

from services_app.forms import TypesServicesForm, ServicesForm
from home_app.forms import AvisReseauForm, VideoTemoignageForm, ActualiteForm
class DirecteurDashboardView(LoginRequiredMixin,UserPassesTestMixin,TemplateView ):
    
    template_name = "directeur_templates/directeur.html"
    
    # test_func est une method qui vient de la classe UserPassTestMixin elle retourne la condition de permissité sur la View
    def test_func(self):
        # Seul le directeur ou superuser peut accéder
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    
    
    # get_context_data est une methode de la class TemplateView permet d'ajouter et de return le context qui accecible depuis le template:
    # avec cette method depuis directeur.htlm on peut acceder au info User qui connecter 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["directeur"] = self.request.user
        
        if "user_register_form" not in context:
            context["user_register_form"] = UserRegisterForm()
        
        if 'change_pass_form' not in context:
            context["change_pass_form"] = ChangePasswordForm()
            
        if 'marque_form' not in context:
            context["marque_form"] = MarqueForm()
        
        if "vehicul_form" not in context:
            context["vehicul_form"] = VehiculForm()
            
        if "create_product_form" not in context:
            context["create_product_form"] = ProductsForm()
        
        if "create_categorie_form" not in context:
            context["create_categorie_form"] = CategorieProductsForm()
        if 'create_unite_form' not in context:
                    context['create_unite_form'] = UniteProduitForm()
        if 'create_product_marque_form' not in context:
                context['create_product_marque_form'] = MarqueProduitForm()
            
        if 'types_services_form' not in context:
            context['types_services_form'] = TypesServicesForm()
            
        if 'services_form' not in context:
            context['services_form'] = ServicesForm()
        # Dans DirecteurDashboardView.get_context_data()
        if "type_vehicul_form" not in context:
            context["type_vehicul_form"] = TypeVehiculeForm()
        
        if "avis_reseau_form" not in context:
            context["avis_reseau_form"] = AvisReseauForm()
            
        if "video_temoignage_form" not in context:
            context["video_temoignage_form"] = VideoTemoignageForm()
        
        if "actualite_form" not in context:
            context["actualite_form"] = ActualiteForm()
            
        return context 
    
class DirecteurRendezVousListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = RendezVous
    template_name = 'directeur_templates/rendez_vous_list.html'
    context_object_name = 'rendez_vous'
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"

    def get_queryset(self):
        queryset = RendezVous.objects.all().order_by('-date_rendez_vous')
        
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
    

        
        
    
  
    
