from rest_framework import serializers
from .models import Panier, ArticlePanier, Commande
from products_app.models import Products

class ArticlePanierSerializer(serializers.ModelSerializer):
    
    produit_nom = serializers.CharField(
        source='products.nom', 
        read_only=True # read_only=True : ce champ est uniquement envoyé au client, jamais reçu du client
        )
    produit_prix = serializers.DecimalField(
        source="products.prix_actuel", 
        read_only=True, max_digits=10,  # read_only=True : ce champ est uniquement envoyé au client, jamais reçu du client
        decimal_places=0
        )
    
    # SerializerMethodField : appelle une méthode pour calculer la valeur
    total_ligne = serializers.SerializerMethodField()
    
    class Meta:
        model = ArticlePanier
        fields = ['id', 'products', 'produit_nom', 'produit_prix', 'quantite', 'total_ligne']
        
    def get_total_ligne(self, obj):
        """
        SerializerMethodField appelle automaitiquement cette methode
        obj=l'instance ArticlePanier en cour de sérialisation 
        """
        return obj.sous_total() # Calcule quantite × prix via la méthode du modèle


# ------------------------------------------------------------
# 2. SÉRIALIZER POUR LE PANIER COMPLET
# ------------------------------------------------------------

class PanierSerializer(serializers.ModelSerializer):
    """ 
        Sérializer pour le panier(client).
        Affiche la liste des articles + total + le nombre d'article    
    """
    # 'articles' est le related_name depuis ArticlePanier → Panier
    # many=True : il y a plusieurs articles
    # read_only=True : ne pas envoyer au client pour modification
    articles = ArticlePanierSerializer(many=True, read_only=True)
    
    # Champs calculés (non stockés en base)
    total = serializers.SerializerMethodField()
    nb_articles = serializers.SerializerMethodField()
    
    class Meta:
        model = Panier
        fields = ['id', 'articles', 'total', 'nb_articles', 'date_creation', 'date_mise_a_jour']
        # date_creation et date_mise_a_jour sont automatiquement gérés par Django
        
    def get_total(self, obj):
        """
        Retourne le montant total du panier
        obj = l'instance Panier 
            """
        return obj.total_panier() # Méthode existante dans le modèle
        
    def get_nb_articles(self, obj):
        """ Retourne le nombre d'article (en comptant les quantité)
        """
        return obj.nb_articles()
    

# ------------------------------------------------------------
# 3. SÉRIALIZER POUR UNE COMMANDE
# ------------------------------------------------------------

class CommandeSerializer(serializers.ModelSerializer):
    """
    Sérializer pour une commande.
    """
    class Meta:
        model = Commande
        fields = ['id', 'statut', 'date_commande', 'paiements']
        # 'paiements' est la relation OneToOne avec Paiement