from django.contrib import admin
from .models import demande_financement, Vente

@admin.register(demande_financement)
class AdminDemandeFinancement(admin.ModelAdmin):
    list_display = ["client", "Vehicul_interested", "etape", "date_creation"]

@admin.register(Vente)
class AdminVente(admin.ModelAdmin):
    list_display = ['client']
    
    
    