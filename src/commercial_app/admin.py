from django.contrib import admin
from .models import Offre

@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin): 
    list_display = ('client', 'vehicule_propose', 'prix_vehicule', 'apport_demande', 'montant_finance', 'duree_mois', 'taux_interet', 'mensualite', 'date_expiration')
    search_fields = ('client__username', 'vehicule_propose')
    list_filter = ('duree_mois', 'taux_interet') 