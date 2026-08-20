from rest_framework import serializers
from .models import kozUser

class RegisterSerializers(serializers.ModelSerializer):
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = kozUser
        fields = [
            "email", 
            "nom_complet", 
            "telephone", 
            "adresse",
            "pays",
            "ville",
            "genre",
            "profession_choisie",
            "password", 
            "password2"
        ]
        
        # ✅ Sécurité : le role est défini par défaut, pas par l'utilisateur
        # ✅ L'ID est auto-généré, pas besoin de le demander
    
    def validate(self, attrs):
        """Vérifie que les mots de passe correspondent"""
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({
                "error": "Les mots de passe ne correspondent pas"
            })
            
        if len(attrs["password"]) < 8:
            raise serializers.ValidationError({
                "error": "Le mot de passe doit contenir au moins 8 caractères"
            })
        
        if attrs["telephone"] and not attrs["telephone"].isdigit():
            raise serializers.ValidationError({
                "error": "Le numéro de téléphone doit contenir uniquement des chiffres"
            })
            
       
            
        return attrs
    
    def create(self, validated_data):
        """Crée l'utilisateur avec les données validées"""
        # ✅ Supprimer password2 (champ virtuel)
        validated_data.pop("password2")
        
        # ✅ Récupérer le password pour le hasher
        password = validated_data.pop("password")
        
        # ✅ Créer l'utilisateur avec le gestionnaire personnalisé
        user = kozUser.objects.create_user(
            email=validated_data.get("email"),
            nom_complet=validated_data.get("nom_complet"),
            telephone=validated_data.get("telephone"),
            password=password,  # ← Le gestionnaire va hasher
            adresse=validated_data.get("adresse", ""),  # ← Optionnel
            pays=validated_data.get("pays", ""),  # ← Optionnel
            ville=validated_data.get("ville", ""),  # ← Optionnel
            genre=validated_data.get("genre", ""),  # ← Optionnel
            profession_choisie=validated_data.get("profession_choisie", ""),  # ← Optionnel
        )
        
        # ✅ Le rôle est déjà "client" par défaut dans le modèle
        # Pas besoin de le définir ici
        
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour afficher les infos d'un utilisateur"""
    class Meta:
        model = kozUser
        fields = [
            'id', 
            'email', 
            'nom_complet', 
            'telephone', 
            'adresse', 
            'pays',
            'ville',
            'genre',
            'profession_choisie',
            'role', 
            'is_staff', 
            'is_active',
            'date_inscription',
            'est_en_ligne',  # ✅ Ajout du statut en ligne
        ]
            
    