from django.contrib import admin
from .models import Documents

@admin.register(Documents)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['client', 'cni_passeport', 'justificatif_domicile', 'relevé_bancaire', 
                  'contrat_travail']