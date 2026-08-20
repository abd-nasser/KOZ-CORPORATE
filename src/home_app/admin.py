from django.contrib import admin

# home_app/admin.py
from django.contrib import admin
from .models import Temoignage, AvisReseau, VideoTemoignage

@admin.register(Temoignage)
class TemoignageTextuelAdmin(admin.ModelAdmin):
    list_display = ['nom', 'est_approuve', 'date_creation']

@admin.register(AvisReseau)
class AvisReseauAdmin(admin.ModelAdmin):
    list_display = ['reseau', 'nom_utilisateur', 'date_publication', 'est_actif']

@admin.register(VideoTemoignage)
class VideoTemoignageAdmin(admin.ModelAdmin):
    list_display = ['titre', 'duree', 'est_actif', 'date_ajout']
    list_filter = ['est_actif']
    search_fields = ['titre', 'description']
    readonly_fields = ['date_ajout']


from django.contrib import admin
from .models import Actualite

class ActualiteAdmin(admin.ModelAdmin):
    list_display = ['titre', 'type', 'date_evenement', 'est_publie', 'est_vedette', 'vues']
    list_filter = ['type', 'est_publie', 'est_vedette', 'date_evenement']
    search_fields = ['titre', 'description', 'sous_titre']
    readonly_fields = ['vues', 'date_creation', 'date_modification']
    ordering = ['-date_evenement']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('titre', 'sous_titre', 'description', 'description_courte', 'type')
        }),
        ('Images', {
            'fields': ('image_principale', 'image_1', 'image_2', 'image_3', 'image_4', 'image_5')
        }),
        ('Vidéo', {
            'fields': ('video_file', 'video_url')
        }),
        ('Liens', {
            'fields': ('lien_externe', 'lien_interne')
        }),
        ('Dates', {
            'fields': ('date_evenement', 'date_publication', 'date_fin')
        }),
        ('Visibilité', {
            'fields': ('est_publie', 'est_vedette', 'ordre')
        }),
        ('Statistiques', {
            'fields': ('vues', 'date_creation', 'date_modification')
        }),
    )

admin.site.register(Actualite, ActualiteAdmin)