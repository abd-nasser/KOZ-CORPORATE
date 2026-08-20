from multiprocessing import context

from django.db.models import Sum, Count, Value, F
from django.db.models.functions import Coalesce
import json
import re
from django.utils import timezone
from datetime import timedelta
from leads_app.models import Vente

from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime, timedelta
from django.db.models import Count, Sum

from django.shortcuts import render
from django.urls import reverse_lazy
from client_app.models import Documents, Maintenance
from commercial_app.models import Offre
from auth_app.models import kozUser
from leads_app.models import demande_financement


class DashboardView(LoginRequiredMixin,TemplateView):
    

    def get_template_names(self):
        is_htmx = self.request.headers.get('HX-Request') == 'true'
        if self.request.user.role == 'directeur' or self.request.user.is_superuser:
            return ['partials/partial_dashboard_directeur.html' if  is_htmx else 'dashboard_templates/directeur_dashboard.html']
        elif self.request.user.role == 'commercial' or self.request.user.is_staff:
            return ['partials/partial_dashboard_commercial.html' if  is_htmx else 'dashboard_templates/commercial_dashboard.html']
       
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser or self.request.user.role == "directeur" or self.request.user.is_staff:
            
            # 📊 KPI Clients
            total_clients = kozUser.objects.filter(role='client').count()
            nb_clients_jour = kozUser.objects.filter(role='client', date_inscription__date=datetime.now().date()).count()
            nb_clients_semaine = kozUser.objects.filter(
                role='client', 
                date_inscription__date__gte=datetime.now().date() - timedelta(days=7)
            ).count()
            
            nb_clients_mois = kozUser.objects.filter(
                role='client', 
                date_inscription__date__gte=datetime.now().date() - timedelta(days=30)
            ).count()

            # Clients avec demande de financement
            clients_avec_demande = kozUser.objects.filter(
                role='client', 
                demande_financement__isnull=False
            ).distinct().count()
            
            # Clients avec offre acceptée
            clients_avec_offre = kozUser.objects.filter(
                role='client', 
                offres__statut='acceptee'
            ).count()
            
            # Taux de conversion (clients → offre acceptée)
            taux_conversion = (clients_avec_offre / total_clients * 100) if total_clients > 0 else 0

            # Top 5 clients (par montant financé)
            top_clients = kozUser.objects.filter(
                role='client', 
                offres__statut='acceptee'
            ).annotate(
                montant_total=Sum('offres__montant_finance')
            ).order_by('-montant_total')[:5]

            context.update({
                'total_clients': total_clients,
                'nb_clients_jour': nb_clients_jour,
                'nb_clients_semaine': nb_clients_semaine,
                'nb_clients_mois': nb_clients_mois,
                'clients_avec_demande': clients_avec_demande,
                'clients_avec_offre': clients_avec_offre,
                'taux_conversion': taux_conversion,
                'top_clients': top_clients,
            })
            
            
            #######################################"" 📊 KPI DEMANDE_FINANCEMENT########################################
            #######################################📊 KPI DEMANDE_FINANCEMENT########################################
            total_demandes = demande_financement.objects.all().count()
            demandes_jour = demande_financement.objects.filter(date_creation__date=datetime.now().date()).count()
            demandes_semaine = demande_financement.objects.filter(date_creation__date__gte=datetime.now().date() - timedelta(days=7)).count()
            demandes_mois = demande_financement.objects.filter(date_creation__date__gte=datetime.now().date() - timedelta(days=30)).count()
            demandes_accorder_fidelis = demande_financement.objects.filter(etape='demande_accordee_fidelis', financement_type="externe").count()
            demandes_accorder_alios = demande_financement.objects.filter(etape='demande_accordee_alios', financement_type="externe").count()
            demandes_accorder_maison = demande_financement.objects.filter(etape='demande_accordee_maison', financement_type="maison").count()
            demandes_refuser = demande_financement.objects.filter(etape='demande_refusee').count()
            demandes_en_cours = demande_financement.objects.filter(etape='en_cours').count()
            demandes_en_attente = demande_financement.objects.filter(etape='en_attente').count()
            taux_accord_fidelis = ((demandes_accorder_fidelis) / total_demandes * 100) if total_demandes > 0 else 0
            taux_accord_alios = ((demandes_accorder_alios) / total_demandes * 100) if total_demandes > 0 else 0
            taux_accord_externe = ((demandes_accorder_fidelis + demandes_accorder_alios) / total_demandes * 100) if total_demandes > 0 else 0
            taux_accord_maison = ((demandes_accorder_maison) / total_demandes * 100) if total_demandes > 0 else 0

            context.update({
                'total_demandes': total_demandes,
                'demandes_jour': demandes_jour,
                'demandes_semaine': demandes_semaine,
                'demandes_mois': demandes_mois,
                'demandes_accorder_fidelis': demandes_accorder_fidelis,
                'demandes_accorder_alios': demandes_accorder_alios,
                'demandes_accorder_maison': demandes_accorder_maison,
                'demandes_refuser': demandes_refuser,
                'demandes_en_cours': demandes_en_cours,
                'demandes_en_attente': demandes_en_attente,
                'taux_accord_fidelis': taux_accord_fidelis,
                'taux_accord_alios': taux_accord_alios,
                'taux_accord_externe': taux_accord_externe,
                'taux_accord_maison': taux_accord_maison,
            })
            
            
            ############################################"KPI DOCUMENTS"########################################
            ############################################"KPI DOCUMENTS"########################################
            total_dossiers = Documents.objects.all().count()
            dossiers_jour = Documents.objects.filter(date_upload__date=datetime.now().date()).count()
            dossiers_semaine = Documents.objects.filter(date_upload__date__gte=datetime.now().date() - timedelta(days=7)).count()
            dossiers_mois = Documents.objects.filter(date_upload__date__gte=datetime.now().date() - timedelta(days=30)).count()
            dossier_vide = Documents.objects.filter(statut_dossier='vide').count()
            dossier_incomplet = Documents.objects.filter(statut_dossier='incomplet').count()
            dossier_complet = Documents.objects.filter(statut_dossier='complet').count()
            dossier_en_verification = Documents.objects.filter(statut_dossier='verification').count()
            dossier_rejete = Documents.objects.filter(statut_dossier='rejete').count()
            dossier_valide = Documents.objects.filter(statut_dossier='valide').count()
            taux_dossier_valide = ((dossier_valide) / total_dossiers * 100) if total_dossiers > 0 else 0
            taux_dossier_rejete = ((dossier_rejete) / total_dossiers * 100) if total_dossiers > 0 else 0
            taux_dossier_en_verification = ((dossier_en_verification) / total_dossiers * 100) if total_dossiers > 0 else 0
            context.update({
                'total_dossiers': total_dossiers,
                'dossiers_jour': dossiers_jour,
                'dossiers_semaine': dossiers_semaine,
                'dossiers_mois': dossiers_mois,
                'dossier_vide': dossier_vide,
                'dossier_incomplet': dossier_incomplet,
                'dossier_complet': dossier_complet,
                'dossier_en_verification': dossier_en_verification,
                'dossier_rejete': dossier_rejete,
                'dossier_valide': dossier_valide,
                'taux_dossier_valide': taux_dossier_valide,
                'taux_dossier_rejete': taux_dossier_rejete,
                'taux_dossier_en_verification': taux_dossier_en_verification,
            })
            
            #########################################"KPI OFFRES"########################################
            #########################################"KPI OFFRES"########################################
            total_offres = Offre.objects.all().count()
            offres_jour = Offre.objects.filter(date_creation__date=datetime.now().date()).count()
            offres_semaine = Offre.objects.filter(date_creation__date__gte=datetime.now().date() - timedelta(days=7)).count()
            offres_mois = Offre.objects.filter(date_creation__date__gte=datetime.now().date() - timedelta(days=30)).count()
            offres_brouillon = Offre.objects.filter(statut='brouillon').count()
            offres_envoyee = Offre.objects.filter(statut='envoyee').count()
            offres_acceptee = Offre.objects.filter(statut__in = ["offre_financement_fidelis",'offre_financement_alios','offre_financement_maison','acceptee']).count()
            offres_refusee = Offre.objects.filter(statut='refusee').count()
            offres_expiree = Offre.objects.filter(statut='expiree').count()
            taux_offre_acceptee = ((offres_acceptee) / total_offres * 100) if total_offres > 0 else 0
            taux_offre_refusee = ((offres_refusee) / total_offres * 100) if total_offres > 0 else 0
            taux_offre_expiree = ((offres_expiree) / total_offres * 100) if total_offres > 0 else 0
            context.update({
                'total_offres': total_offres,
                'offres_jour': offres_jour,
                'offres_semaine': offres_semaine,
                'offres_mois': offres_mois,
                'offres_brouillon': offres_brouillon,
                'offres_envoyee': offres_envoyee,
                'offres_acceptee': offres_acceptee,
                'offres_refusee': offres_refusee,
                'offres_expiree': offres_expiree,
                'taux_offre_acceptee': taux_offre_acceptee,
                'taux_offre_refusee': taux_offre_refusee,
                'taux_offre_expiree': taux_offre_expiree,
            })
            
            #########################################"""KPI MAINTENANCE"""########################################
            #########################################"""KPI MAINTENANCE"""########################################
            
            total_maintenances = Maintenance.objects.all().count()
            maintenances_jour = Maintenance.objects.filter(date_creation__date=datetime.now().date()).count()
            maintenances_semaine = Maintenance.objects.filter(date_creation__date__gte=datetime.now().date() - timedelta(days=7)).count()
            maintenances_mois = Maintenance.objects.filter(date_creation__date__gte=datetime.now().date() - timedelta(days=30)).count()
            maintenances_effectuee = Maintenance.objects.filter(statut='effectuee').count()
            maintenances_annulee = Maintenance.objects.filter(statut='annulee').count()
            maintenances_acceptee = Maintenance.objects.filter(statut='confirme').count()
            maintenances_planifiee = Maintenance.objects.filter(statut='planifiee').count()
            maintenances_en_cours = Maintenance.objects.filter(statut='en_cours').count()
            taux_maintenance_effectuee = ((maintenances_effectuee) / total_maintenances * 100) if total_maintenances > 0 else 0
            taux_maintenance_annulee = ((maintenances_annulee) / total_maintenances * 100) if total_maintenances > 0 else 0
            taux_maintenance_acceptee = ((maintenances_acceptee) / total_maintenances * 100) if total_maintenances > 0 else 0
            taux_maintenance_planifiee = ((maintenances_planifiee) / total_maintenances * 100) if total_maintenances > 0 else 0
            taux_maintenance_en_cours = ((maintenances_en_cours) / total_maintenances * 100) if total_maintenances > 0 else 0
            
            context.update({
                'total_maintenances': total_maintenances,
                'maintenances_jour': maintenances_jour,
                'maintenances_semaine': maintenances_semaine,
                'maintenances_mois': maintenances_mois,
                'maintenances_effectuee': maintenances_effectuee,
                'maintenances_annulee': maintenances_annulee,
                'maintenances_acceptee': maintenances_acceptee,
                'maintenances_planifiee': maintenances_planifiee,
                'maintenances_en_cours': maintenances_en_cours,
                'taux_maintenance_effectuee': taux_maintenance_effectuee,
                'taux_maintenance_annulee': taux_maintenance_annulee,
                'taux_maintenance_acceptee': taux_maintenance_acceptee,
                'taux_maintenance_planifiee': taux_maintenance_planifiee,
                'taux_maintenance_en_cours': taux_maintenance_en_cours,
            })
        
            
        

            
            ##################____QUERYSET CLIENTS____################################################"
            # ###################____QUERYSET CLIENTS____################################################"
            total_clients_queryset = kozUser.objects.filter(role='client')
            nb_clients_jour_queryset = kozUser.objects.filter(role='client', date_inscription__date=datetime.now().date())
            nb_clients_semaine_queryset = kozUser.objects.filter(   role='client', date_inscription__date__gte=datetime.now().date() - timedelta(days=7))
            nb_clients_mois_queryset = kozUser.objects.filter(   role='client', date_inscription__date__gte=datetime.now().date() - timedelta(days=30))
            clients_avec_demande_queryset = kozUser.objects.filter(   role='client', demande_financement__isnull=False).distinct()
            clients_avec_offre_queryset = kozUser.objects.filter(   role='client', offres__statut='acceptee')
            top_clients_queryset = kozUser.objects.filter(   role='client', offres__statut='acceptee').annotate(montant_total=Sum('offres__montant_finance')).order_by('-montant_total')[:5]
            
            context.update({
                'total_clients_queryset': total_clients_queryset,
                'nb_clients_jour_queryset': nb_clients_jour_queryset,
                'nb_clients_semaine_queryset': nb_clients_semaine_queryset,
                'nb_clients_mois_queryset': nb_clients_mois_queryset,
                'clients_avec_demande_queryset': clients_avec_demande_queryset,
                'clients_avec_offre_queryset': clients_avec_offre_queryset,
                'top_clients_queryset': top_clients_queryset
            })

            #############################____QUERYSET DEMANDE_FINANCEMENT____################################################"
            total_demandes_queryset = demande_financement.objects.all()
            demandes_jour_queryset = demande_financement.objects.filter(date_creation__date=datetime.now().date())
            demandes_semaine_queryset = demande_financement.objects.filter(date_creation__date__gte=datetime.now().date() - timedelta(days=7))
            demandes_mois_queryset = demande_financement.objects.filter(date_creation__date__gte=datetime.now().date() - timedelta(days=30))
            demandes_accorder_fidelis_queryset = demande_financement.objects.filter(etape='accordee_fidelis', financement_type="externe")
            demandes_accorder_alios_queryset = demande_financement.objects.filter(etape='accordee_alios', financement_type="externe")
            demandes_accorder_maison_queryset = demande_financement.objects.filter(etape='accordee_maison', financement_type="maison")
            demandes_refuser_queryset = demande_financement.objects.filter(etape='refusee') 
            demandes_en_cours_queryset = demande_financement.objects.filter(etape='en_cours')
            demandes_en_attente_queryset = demande_financement.objects.filter(etape='en_attente')
            
            context.update({
                'total_demandes_queryset': total_demandes_queryset,
                'demandes_jour_queryset': demandes_jour_queryset,
                'demandes_semaine_queryset': demandes_semaine_queryset,
                'demandes_mois_queryset': demandes_mois_queryset,
                'demandes_accorder_fidelis_queryset': demandes_accorder_fidelis_queryset,
                'demandes_accorder_alios_queryset': demandes_accorder_alios_queryset,
                'demandes_accorder_maison_queryset': demandes_accorder_maison_queryset,
                'demandes_refuser_queryset': demandes_refuser_queryset,
                'demandes_en_cours_queryset': demandes_en_cours_queryset,
                'demandes_en_attente_queryset': demandes_en_attente_queryset
            })

            #############################____QUERYSET DOCUMENTS____################################################"
            total_dossiers_queryset = Documents.objects.all()
            dossiers_jour_queryset = Documents.objects.filter(date_upload__date=datetime.now().date())
            dossiers_semaine_queryset = Documents.objects.filter(date_upload__date__gte=datetime.now().date() - timedelta(days=7))
            dossiers_mois_queryset = Documents.objects.filter(date_upload__date__gte=datetime.now().date() - timedelta(days=30))
            dossier_vide_queryset = Documents.objects.filter(statut_dossier='vide') 
            dossier_incomplet_queryset = Documents.objects.filter(statut_dossier='incomplet')
            dossier_complet_queryset = Documents.objects.filter(statut_dossier='complet')
            dossier_en_verification_queryset = Documents.objects.filter(statut_dossier='verification')
            dossier_rejete_queryset = Documents.objects.filter(statut_dossier='rejete')
            dossier_valide_queryset = Documents.objects.filter(statut_dossier='valide')
            
            context.update({
                'total_dossiers_queryset': total_dossiers_queryset,
                'dossiers_jour_queryset': dossiers_jour_queryset,
                'dossiers_semaine_queryset': dossiers_semaine_queryset,
                'dossiers_mois_queryset': dossiers_mois_queryset,
                'dossier_vide_queryset': dossier_vide_queryset,
                'dossier_incomplet_queryset': dossier_incomplet_queryset,
                'dossier_complet_queryset': dossier_complet_queryset,
                'dossier_en_verification_queryset': dossier_en_verification_queryset,
                'dossier_rejete_queryset': dossier_rejete_queryset,
                'dossier_valide_queryset': dossier_valide_queryset
            })
            
            #############################____QUERYSET OFFRES____################################################"
            total_offres_queryset = Offre.objects.all()
            offres_jour_queryset = Offre.objects.filter(date_creation__date=datetime.now().date())
            offres_semaine_queryset = Offre.objects.filter(date_creation__date__gte=datetime.now().date() - timedelta(days=7))
            offres_mois_queryset = Offre.objects.filter(date_creation__date__gte=datetime.now().date() - timedelta(days=30))
            offres_brouillon_queryset = Offre.objects.filter(statut='brouillon')    
            offres_envoyee_queryset = Offre.objects.filter(statut='envoyee')
            offres_acceptee_queryset = Offre.objects.filter(statut='acceptee')
            offres_refusee_queryset = Offre.objects.filter(statut='refusee')
            offres_expiree_queryset = Offre.objects.filter(statut='expiree')
            
            context.update({
                'total_offres_queryset': total_offres_queryset,
                'offres_jour_queryset': offres_jour_queryset,
                'offres_semaine_queryset': offres_semaine_queryset,
                'offres_mois_queryset': offres_mois_queryset,
                'offres_brouillon_queryset': offres_brouillon_queryset, 
                'offres_envoyee_queryset': offres_envoyee_queryset,
                'offres_acceptee_queryset': offres_acceptee_queryset,       
                'offres_refusee_queryset': offres_refusee_queryset,
                'offres_expiree_queryset': offres_expiree_queryset})
            
            #############################____QUERYSET MAINTENANCE____################################################"
            total_maintenances_queryset = Maintenance.objects.all()
            maintenances_jour_queryset = Maintenance.objects.filter(date_creation__date=datetime.now().date())
            maintenances_semaine_queryset = Maintenance.objects.filter(date_creation__date__gte=datetime.now().date() - timedelta(days=7))
            maintenances_mois_queryset = Maintenance.objects.filter(date_creation__date__gte=datetime.now().date() - timedelta(days=30))
            maintenances_effectuee_queryset = Maintenance.objects.filter(statut='effectuee')
            maintenances_annulee_queryset = Maintenance.objects.filter(statut='annulee')
            maintenances_acceptee_queryset = Maintenance.objects.filter(statut='confirme')
            maintenances_planifiee_queryset = Maintenance.objects.filter(statut='planifiee')
            maintenances_en_cours_queryset = Maintenance.objects.filter(statut='en_cours')
            
            context.update({
                'total_maintenances_queryset': total_maintenances_queryset,
                'maintenances_jour_queryset': maintenances_jour_queryset,
                'maintenances_semaine_queryset': maintenances_semaine_queryset,
                'maintenances_mois_queryset': maintenances_mois_queryset,
                'maintenances_effectuee_queryset': maintenances_effectuee_queryset,
                'maintenances_annulee_queryset': maintenances_annulee_queryset,
                'maintenances_acceptee_queryset': maintenances_acceptee_queryset,
                'maintenances_planifiee_queryset': maintenances_planifiee_queryset,
                'maintenances_en_cours_queryset': maintenances_en_cours_queryset
            })
            
       
        # Tu peux copier-coller les mêmes blocs que pour le directeur
        # pour demandes, offres, documents, maintenances
        # en ajoutant à chaque fois .filter(client__assigned_commercial=self.request.user)
        # ============================================
     
     
     
        # 📊 CHART LINE : Évolution du CA par type de vente
        # ============================================================
        # 1. Définition des périodes
        # ============================================================
        now = timezone.now()
        periods = {
            '1j': now - timedelta(days=1),
            '7j': now - timedelta(days=7),
            '1m': now - timedelta(days=30),
            '1y': now - timedelta(days=365),
        }

        # ============================================================
        # 2. Période sélectionnée
        # ============================================================
        selected_period = self.request.GET.get('period', '1m')
        start_date = periods.get(selected_period, periods['1m'])

        # ============================================================
        # 3. Récupération des ventes conclues
        # ============================================================
        ventes = Vente.objects.filter(
            statut__in=[
                "conclue",
                "conclue_par_acceptation_offre_simple",
                "conclue_par_acceptation_offre_financement",
                "conclue_sur_acceptation_demande_financement",
            ],
            date_vente__gte=start_date
        ).select_related('demande_financement', 'offre')

        # ============================================================
        # 4. Regroupement des données
        # ============================================================
        if selected_period == '1y':
            # ---------- Période 1 an → par MOIS ----------
            ventes_par_mois = {}
            
            for vente in ventes:
                mois = vente.date_vente.strftime('%b %Y')
                
                if mois not in ventes_par_mois:
                    ventes_par_mois[mois] = {
                        'fidelis': 0,
                        'alios': 0,
                        'maison': 0,
                        'cash': 0,
                        'total': 0,  # ✅ AJOUT
                        
                    }
                
                # ✅ Utiliser la propriété type_vente
                type_vente = vente.type_vente
                
                # ✅ ✅ ✅ UTILISER montant_total_paye (CA réel)
                montant_a_ajouter = int(vente.montant_total_paye) if vente.montant_total_paye else int(vente.montant)
                if type_vente == 'externe_fidelis':
                    ventes_par_mois[mois]['fidelis'] += montant_a_ajouter
                elif type_vente == 'externe_alios':
                    ventes_par_mois[mois]['alios'] += montant_a_ajouter
                    
                elif type_vente == 'maison':
                    ventes_par_mois[mois]['maison'] += montant_a_ajouter
                    
                elif type_vente == 'cash':
                    ventes_par_mois[mois]['cash'] += montant_a_ajouter
                    
                # ✅ AJOUTER AU TOTAL
                ventes_par_mois[mois]['total'] += montant_a_ajouter
            labels = list(ventes_par_mois.keys())
            context['chart_labels'] = json.dumps(labels)
            context['chart_fidelis'] = json.dumps([ventes_par_mois[m]['fidelis'] for m in labels])
            context['chart_alios'] = json.dumps([ventes_par_mois[m]['alios'] for m in labels])
            context['chart_maison'] = json.dumps([ventes_par_mois[m]['maison'] for m in labels])
            context['chart_cash'] = json.dumps([ventes_par_mois[m]['cash'] for m in labels])
            context['chart_total'] = json.dumps([ventes_par_mois[m]['total'] for m in labels])  # ✅ AJOUT
            context['selected_period'] = selected_period

        else:
            # ---------- Période courte → par JOUR ----------
            ventes_par_jour = {}
            
            for vente in ventes:
                jour = vente.date_vente.strftime('%d/%m')
                
                if jour not in ventes_par_jour:
                    ventes_par_jour[jour] = {
                        'fidelis': 0,
                        'alios': 0,
                        'maison': 0,
                        'cash': 0,
                        'total': 0, 
                    }
                
                # ✅ Utiliser la propriété type_vente
                type_vente = vente.type_vente
                 # ✅ ✅ ✅ UTILISER montant_total_paye (CA réel)
                montant_a_ajouter = int(vente.montant_total_paye) if vente.montant_total_paye else int(vente.montant)
                if type_vente == 'externe_fidelis':
                    ventes_par_jour[jour]['fidelis'] += montant_a_ajouter
                elif type_vente == 'externe_alios':
                    ventes_par_jour[jour]['alios'] += montant_a_ajouter
                elif type_vente == 'maison':
                    ventes_par_jour[jour]['maison'] += montant_a_ajouter
                elif type_vente == 'cash':
                    ventes_par_jour[jour]['cash'] += montant_a_ajouter
                    
                ventes_par_jour[jour]['total'] += montant_a_ajouter
            labels = list(ventes_par_jour.keys())
            context['chart_labels'] = json.dumps(labels)
            context['chart_fidelis'] = json.dumps([ventes_par_jour[j]['fidelis'] for j in labels])
            context['chart_alios'] = json.dumps([ventes_par_jour[j]['alios'] for j in labels])
            context['chart_maison'] = json.dumps([ventes_par_jour[j]['maison'] for j in labels])
            context['chart_cash'] = json.dumps([ventes_par_jour[j]['cash'] for j in labels])
            context['chart_total'] = json.dumps([ventes_par_jour[j]['total'] for j in labels])  # ✅ AJOUT
            context['selected_period'] = selected_period
            print(context['chart_labels'])

        # ============================================================
        # 5. Statistiques globales
        # ============================================================
       
        total_simple = 0
        total_autres = 0

        for vente in ventes:
            if vente.type_vente == "cash":  # simple
                total_simple += float(vente.montant or 0)
            else:
                total_autres += float(vente.montant_total_paye or 0)

        total_ca = total_simple + total_autres
        context['total_ca'] = total_ca
        context['nb_ventes']  = ventes.count()
        return context
        
        
        
        
    
class ListeFiltreeView(ListView):
    template_name = 'dashboard_templates/liste_filtree.html'
    context_object_name = 'items'
    
    def _parse_filter_value(self, filter_nom, filter_valeur):
        if isinstance(filter_valeur, str):
            valeur = filter_valeur.strip()
            if filter_nom.endswith('__isnull'):
                return valeur.lower() in ('true', '1', 'yes', 'y', 't')
            if valeur.lower() in ('none', 'null'):
                return None
            if re.fullmatch(r'-?\d+', valeur):
                return int(valeur)
            if re.fullmatch(r'-?\d+\.\d+', valeur):
                return float(valeur)
        return filter_valeur

    def get_queryset(self):
        model_name = self.kwargs.get('model_name')
        filter_nom = self.kwargs.get('filter_nom')
        filter_valeur = self._parse_filter_value(filter_nom, self.kwargs.get('filter_valeur'))
        
        user = self.request.user
        
        # Base queryset selon le modèle
        if model_name == 'offres':
            queryset = Offre.objects.filter(**{filter_nom: filter_valeur}).order_by('-date_creation')
            
            # 👇 AJOUTE ÇA
            #if user.role == 'commercial' or user.is_staff:
                #queryset = queryset.filter(client__assigned_commercial=user)
            # Pour le directeur, on garde tout
            
            return queryset
        
        if model_name == 'demande_financement':
            queryset = demande_financement.objects.filter(**{filter_nom: filter_valeur})
            #if user.role == 'commercial' or user.is_staff:
                #queryset = queryset.filter(client__assigned_commercial=user)
            return queryset
        
        if model_name == 'documents':
            queryset = Documents.objects.filter(**{filter_nom: filter_valeur}).order_by('-date_upload')
           # if user.role == 'commercial' or user.is_staff:
                #queryset = queryset.filter(client__assigned_commercial=user)
            return queryset
        
        if model_name == 'maintenance':
            queryset = Maintenance.objects.filter(**{filter_nom: filter_valeur})
           # if user.role == 'commercial' or user.is_staff:
              #  queryset = queryset.filter(client__assigned_commercial=user)
            return queryset
        
        if model_name in  ['client', "clients"]:
            queryset = kozUser.objects.filter(**{filter_nom: filter_valeur})
            # Pour les clients, pas de filtrage supplémentaire
            return queryset
        
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name = self.kwargs.get('model_name')
        filter_nom = self.kwargs.get('filter_nom')
        filter_valeur = self.kwargs.get('filter_valeur')

        context['model_name'] = model_name
        context['filter_nom'] = filter_nom
        context['filter_valeur'] = filter_valeur
        context['titre'] = self._build_title(model_name, filter_nom, filter_valeur)
        return context

    def _build_title(self, model_name, filter_nom, filter_valeur):
        labels = {
            'offre': 'offres',
            'offres': 'offres',
            'demande_financement': 'demandes de financement',
            'documents': 'dossiers documentaires',
            'maintenance': 'maintenances',
            'client': 'clients',
            'clients': 'clients',
        }
        model_label = labels.get(model_name, model_name.replace('_', ' ').capitalize())
        if filter_nom and filter_valeur is not None:
            if filter_nom.endswith('__isnull'):
                if str(filter_valeur).lower() in ('true', '1', 'yes', 'y', 't'):
                    return f"{model_label.capitalize()} filtrés : champ '{filter_nom}' vide"
                return f"{model_label.capitalize()} filtrés : champ '{filter_nom}' non vide"
            return f"{model_label.capitalize()} filtrés par {filter_nom.replace('_', ' ')} = {filter_valeur}"
        return f"{model_label.capitalize()} filtrés"