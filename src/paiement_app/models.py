from django.db import models
from order_app.models import Commande

class Paiement(models.Model):
    # 1. Comment on paye ?
    METHOD = [
        ("carte_ligdicash", "Carte Bancaire(ligdicash)"),
        ("mobile_ligdicash", "Mobile Money (Ligdicash)"),
    ]
    
    # 2. Est ce que ça marché ?
    STATUS = [
        ('en_attente',"Attente"),
        ("reussi", "Reussi"),
        ("echec","Echoué"),
        ("annule","Annule"),
        ("paye", "payée")
    ]
    
    # 3. A quelle commande ce paiement est il lié ?
    commande = models.ForeignKey(Commande, related_name="paiement", on_delete=models.CASCADE)
    
    # 4. Avec quel moyen de paiement ?
    methode = models.CharField(max_length=20, choices=METHOD)
    
    # 5. Combien d'argent ?
    montant = models.DecimalField(max_digits=10, decimal_places=2)

    # 6. Ou en est-on ?
    statut = models.CharField(max_length=20,choices=STATUS, default="en_attente")
    
    # 7 Quand est-ce que le paiement à été crée ?
    date_creation = models.DateTimeField(auto_now_add=True)
    
    # 8. Token
    token = models.CharField()
    

    # 9. est ce avec le telephone (ligdicash)
    ligdicash_transaction_id = models.CharField(max_length=100, blank=True)
    ligdicash_phone = models.CharField(max_length=20, blank=True)
    ligdicash_payment_method = models.CharField(max_length=50, blank=True), #card ou mobile_money
