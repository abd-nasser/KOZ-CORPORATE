from django.contrib import admin
from .models import Paiement
# Register your models here.

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ['commande', 'methode', 'montant', 'statut', 'date_creation']
    list_filter = ['methode', 'statut', 'date_creation']
    search_fields = ['commande__id', 'commande__client__nom', 'commande__client__email']
    readonly_fields = ['date_creation']