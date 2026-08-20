from django.db import models
from auth_app.models import kozUser

# chat_app/models.py

class Message(models.Model):
    client = models.ForeignKey(
        kozUser, 
        on_delete=models.CASCADE, 
        related_name="messages_envoyes", 
        limit_choices_to={'role': 'client'}
    )
     
    # ✅ On garde le champ commercial mais on le rend NULLABLE et NON BLOQUANT
    # → Il servira pour l'historique, mais ne limitera plus l'affichage
    commercial = models.ForeignKey(
        kozUser, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,  # ← AJOUT
        related_name="messages_recus", 
        limit_choices_to={"role": 'commercial'}
    )
    
    contenu = models.TextField()
    est_client = models.BooleanField(default=True)
    lu = models.BooleanField(default=False)  # ⚠️ Changé à False par défaut
    date_envoi = models.DateTimeField(auto_now_add=True)
    
    origine_automatique = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['date_envoi']
    


