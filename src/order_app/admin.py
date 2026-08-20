from django.contrib import admin
from .models import Commande
@admin.register(Commande)
class AdminCommande(admin.ModelAdmin):
    list_display = ["panier", "statut", "paiements"]