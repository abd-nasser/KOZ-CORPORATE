from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import TypesServices, Services, ServiceImages, ServiceAvis

class ServiceImagesInline(admin.TabularInline):
    model = ServiceImages
    extra = 3
    fields = ['image', 'alt_text', 'ordre', 'est_principale']


class ServicesAdmin(admin.ModelAdmin):
    list_display = ['nom', 'types', 'prix', 'est_disponible', 'est_vedette', 'date_ajout']
    list_filter = ['types', 'est_disponible', 'est_vedette', 'periodicite']
    search_fields = ['nom', 'description', 'compatible_vehicules']
    filter_horizontal = ['services_inclus']
    inlines = [ServiceImagesInline]


class TypesServicesAdmin(admin.ModelAdmin):
    list_display = ['nom', 'icone', 'est_actif', 'date_ajout']
    search_fields = ['nom']


admin.site.register(TypesServices, TypesServicesAdmin)
admin.site.register(Services, ServicesAdmin)
admin.site.register(ServiceAvis)