from django.db import models
from auth_app.models import kozUser
from products_app.models import Products


 
class Panier(models.Model):
    """Un panier appartient à un client """
    client = models.OneToOneField(kozUser, on_delete=models.CASCADE,related_name="panier")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    
    def total_panier(self):
        return sum(article.sous_total() for article in self.articles.all())

     # 👇 AJOUTER CETTE MÉTHODE 
    def nb_articles(self):
        """Retourne le nombre total d'articles (en comptant les quantités)"""
        return sum(article.quantite for article in self.articles.all())
    def __str__(self):
        return self.client.nom_complet

class ArticlePanier(models.Model):
    """plusieur article ou un article dans le panier"""
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE, related_name="articles")
    products = models.ForeignKey(Products, on_delete=models.CASCADE,related_name="dans_panier")
    quantite = models.IntegerField(db_default=1)
    
    
    def sous_total(self):
        return self.quantite * self.products.prix_actuel
    

class Commande(models.Model):
    STATUT_COMMANDE = [
        ("validee", "Validée"),
        ("annulee", "Annulée"),
        ("payee", "Payée"),
        ("livraison", "En livraison"),
        ("terminee", "Terminée"),
    ]
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE, related_name="commande")
    statut = models.CharField(max_length=20, choices=STATUT_COMMANDE, default="Chargement")
    date_commande = models.DateTimeField(auto_now_add=True)
    paiements = models.OneToOneField("paiement_app.Paiement", related_name="commande_paiement", on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f" commande : {self.panier.client.nom_complet}-{self.statut}"