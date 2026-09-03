from django.contrib import admin
from .models import Documents,Maintenance

@admin.register(Documents)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['client', 'cni_passeport', 'justificatif_domicile', 'relevé_bancaire', 
                  'contrat_travail']
 
@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ['client', 'vehicul', 'date_prevue', 'type_maintenance', 'statut']
 

