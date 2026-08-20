from django.contrib import admin
from .models import Message

# Register your models here.
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'commercial', 'contenu', 'date_envoi', 'est_client')
    list_filter = ('date_envoi', 'est_client')
    search_fields = ('client__username', 'commercial__username', 'contenu')
