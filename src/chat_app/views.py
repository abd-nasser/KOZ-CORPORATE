from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods

from django.http import HttpResponse
from datetime import timedelta
from django.utils import timezone
from auth_app.models import kozUser
from .models import Message
@login_required
def chat_view(request, client_id=None):
    if request.user.role == "client":
        messages = Message.objects.filter(client=request.user).order_by('date_envoi')
        # Calculer le seuil de dernière activité (5 minutes)
        threshold = timezone.now() - timedelta(minutes=5)
        # Récupérer le premier commercial en ligne, trié par dernière activité
        destinataire = kozUser.objects.filter(role="commercial", last_activity__gt=threshold, is_active=True).order_by('-last_activity').first()
        
        # ✅ Marquer les messages comme lus (pour le client
        messages.filter(est_client=False, lu=False).update(lu=True)
        context = {
            'messages': messages,
            'destinataire': destinataire,
            'client_id': request.user.id,
            'client': request.user,
        }
    else:
        # ✅ Commercial : voir tous les messages de tous les clients
        if client_id:
            client = get_object_or_404(kozUser, id=client_id, role="client")
            messages = Message.objects.filter(client=client).order_by('date_envoi')
            
            # ✅ Marquer les messages comme lus (pour le commercial)
            messages.filter(est_client=True, lu=False).update(lu=True)
           
        else:
            # Si aucun client sélectionné, on affiche la liste des clients
            clients = kozUser.objects.filter(role="client")
            messages = None
            client = None
          
        context = {
            'messages': messages,
            'clients': clients if not client_id else None,
            'client': client if client_id else None,
            'client_id': client_id,
        }
    
    return render(request, "chat_templates/chat.html", context)
 
 
@login_required
@require_http_methods(["POST"])
def envoyer_message(request, client_id=None):
    contenu = request.POST.get("contenu")
    if not contenu or not contenu.strip():
        return HttpResponse('')
    
    if request.user.role == "client":
        client = request.user
        commercial = client.assigned_commercial
        message = Message.objects.create(
            client=client,
            commercial=commercial,
            contenu=contenu.strip(),
            est_client=True
        )
    else:
        # ✅ Commercial peut répondre à n'importe quel client
        client = get_object_or_404(kozUser, id=client_id, role="client")
        message = Message.objects.create(
            client=client,
            commercial=request.user,  # ← On garde le commercial qui répond
            contenu=contenu.strip(),
            est_client=False
        )
    
    return render(request, "partials/chat/message.html", {
        'message': message,
        'client': client,
    })