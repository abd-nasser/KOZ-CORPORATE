from rest_framework import serializers
from .models import Paiement

class PaiementSerializer(serializers.ModelSerializer):
    """
    Sérializer pour un paiement Ligdicash.
    """

    class Meta:
        model = Paiement
        fields = [
            'id', 'methode', 'montant', 'statut', 
            'date_creation', 'ligdicash_transaction_id', 
            'ligdicash_phone', 'ligdicash_payment_method'
        ]
        # 'statut' = statut du paiement (en_attente, reussi, echec, annule)
        # 'methode' = carte_ligdicash ou mobile_ligdicash