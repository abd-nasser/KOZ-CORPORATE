from rest_framework import serializers
from .models import demande_financement, Vente, DevisLeads

class DemandeFinancementSerializers(serializers.ModelSerializer):
    mensualite_souhaitee = serializers.DecimalField(
        max_digits=12,
        decimal_places=0,
        required=False,
        allow_null = True,
        help_text="Mensualité souhaitée par le client (FCFA)"
    )
    class Meta:
        model = demande_financement
        fields = [
        'id',
        'client',
        'mensualite_souhaitee',
        'apport',
        'duree_mois',
        'revenus_mensuel',
        'Vehicul_interested',
        'etape',
        'date_creation',
        ]
        
        read_only_fields = [
        'id',
        'client',
        'statut',
        'etape',
        'date_creation',
        ]
        
        extra_kwargs = {
            'vehicul_interested':{'required': False, 'allow_null': True},
            'apport': {'required': False, 'allow_null': True},
            'revenus_mensuel': {'required': False, 'allow_null': True},
            'type_financement': {'required': False, 'allow_null': True},
            'financement_par': {'required': False, 'allow_null': True},
            
            
        }
    
    def validate(self, data):
        """ 
          Validation niveau formulaire (équivalent au clean() de DemandeFinancementForm)
        """
        apport = data.get("apport")
        revenus = data.get("revenus_mensuel")
        vehicule = data.get("Vehicul_interested")
        
        
        if apport is not None and apport <= 0:
            raise serializers.ValidationError({
                "apport":"L'apport ne peut pas etre negatif ou nul"
            })
        if revenus is not None and revenus <= 0:
            raise serializers.ValidationError({
            "revenus_mensuel": "Les revenus mensuels ne peuvent pas être négatifs ou nuls."
        })
            
        if vehicule and apport:
            prix = getattr(vehicule, 'prix', 0)
            if apport > prix:
                raise serializers.ValidationError({
                    "apport": f"L'apport ne peut pas dépasser le prix du véhicule ({prix} FCFA)."
                })
            
        
        return data 
    def validate_apport(self, value):
        """Vérification spécifique pour l'apport"""
        if value is None:
            return value
        if value < 0:
            raise serializers.ValidationError("L'apport ne peut pas être négatif.")
        return value
    
    def create(self, validated_data):
        """Surcharge pour gérer les champs de simulation (non persistants)"""
        validated_data.pop('mensualite_souhaitee', None)
        validated_data.pop('taux_interet', None)
        
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['client'] = request.user
        
        return super().create(validated_data)
            
        
            