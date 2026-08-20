from django.contrib import admin
from client_app.models import Maintenance

@admin.register(Maintenance)
class AdminMaintenance(admin.ModelAdmin):
    list_display = ["client", "statut"]
