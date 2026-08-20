from django.contrib import admin
from .models import kozUser

@admin.register(kozUser)
class AuthAdmin(admin.ModelAdmin):
    list_display=["email", "nom_complet", "telephone", "adresse", "role", "is_active"]
    
