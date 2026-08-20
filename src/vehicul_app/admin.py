from django.contrib import admin
from .models import Marque, Vehicul, VehiculeImage

# ========== INLINE : Images du véhicule ==========
class VehiculeImageInline(admin.TabularInline):
    model = VehiculeImage
    extra = 3
    fields = ['image', 'alt_text', 'ordre', 'est_principale']
    show_change_link = True


@admin.register(Marque)
class MarqueAdmin(admin.ModelAdmin):
    list_display = ['nom', 'id']
    search_fields = ['nom']


from django.contrib import admin
from .models import Marque, Vehicul, VehiculeImage, TypeVehicule

@admin.register(TypeVehicule)
class TypeVehiculeAdmin(admin.ModelAdmin):
    list_display = ['nom', 'icone', 'ordre', 'date_ajout']
    search_fields = ['nom']
    list_editable = ['ordre']

@admin.register(Vehicul)
class VehiculAdmin(admin.ModelAdmin):
    list_display = ['marque', 'type_vehicule', 'modele', 'annee', 'prix', 'disponible']
    list_filter = ['marque', 'type_vehicule', 'carburant', 'disponible', 'annee']
    search_fields = ['marque__nom', 'modele', 'description']
    readonly_fields = ['date_ajout']
    inlines = [VehiculeImageInline]

# ... le reste

@admin.register(VehiculeImage)
class VehiculeImageAdmin(admin.ModelAdmin):
    list_display = ['vehicule', 'image', 'ordre', 'est_principale', 'date_ajout']
    list_filter = ['est_principale', 'vehicule']
    search_fields = ['vehicule__marque__nom', 'vehicule__modele', 'alt_text']
