from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Panier, ArticlePanier, Commande
from products_app.models import Products, CategorieProducts
from .serializers import PanierSerializer, ArticlePanierSerializer, CommandeSerializer


# order_app/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Panier, ArticlePanier, Commande
from products_app.models import Products


@login_required
def panier_view(request):
    """Affiche le panier du client"""
    panier, created = Panier.objects.get_or_create(client=request.user)
    commande = panier.commande.order_by('-date_commande').first()
    return render(request, 'order_templates/panier.html', {'panier': panier,
                                                           'commande': commande})

@login_required
def ajouter_article(request, product_id):
    produit = get_object_or_404(Products, id=product_id)
    panier, _ = Panier.objects.get_or_create(client=request.user)
    
    # ✅ VÉRIFICATION : est-ce qu'une commande est en cours ?
    commande_active = Commande.objects.filter(
        panier=panier,
        statut__in=['validee', 'payee', 'livraison', 'terminee']
    ).first()
    
    if commande_active:
        messages.error(request, f"❌ Vous avez déjà une commande en cours de {commande_active.get_statut_display()}. Vous ne pouvez pas modifier le panier.")
        return redirect('order_app:panier')
    
    # ✅ Ajout normal
    article, created = ArticlePanier.objects.get_or_create(
        panier=panier,
        products=produit,
        defaults={'quantite': 1}
    )
    
    if not created:
        article.quantite += 1
        article.save()
        messages.success(request, f"✅ Quantité augmentée pour {produit.nom}")
    else:
        messages.success(request, f"✅ {produit.nom} ajouté au panier")
    
    return redirect('order_app:panier')
        
        
    
    
@login_required
def modifier_quantite(request, article_id):
    article = get_object_or_404(ArticlePanier, id=article_id, panier__client=request.user)
    
    # ✅ Récupérer la nouvelle quantité depuis le body POST
    quantite = request.POST.get('quantite')  # ← hx-vals envoie 'quantite'
    
    if quantite is not None:
        quantite = int(quantite)
        if quantite <= 0:
            article.delete()
        else:
            article.quantite = quantite
            article.save()
    
    # ✅ Retourner le panier mis à jour
    panier = Panier.objects.get(client=request.user)
    commande = panier.commande.order_by('-date_commande').first()
    return render(request, 'partials/order/panier_container.html', {'panier': panier,
                                                                    'commande': commande})

@login_required
def retirer_article(request, article_id):
    """Supprime un article du panier (HTMX)"""
    article = get_object_or_404(ArticlePanier, id=article_id, panier__client=request.user)
    article.delete()
    return panier_view(request)


@login_required
def vider_panier(request):
    """Vide tout le panier (HTMX)"""
    panier = get_object_or_404(Panier, client=request.user)
    panier.articles.all().delete()
    return panier_view(request)


@login_required
def valider_commande(request):
    """Valide la commande et crée une commande"""
    panier = get_object_or_404(Panier, client=request.user)
    
    if not panier.articles.exists():
        messages.error(request, "❌ Votre panier est vide.")
        return redirect('order_app:panier')
    
    # ✅ Vérifier si une commande existe déjà (pas seulement "Chargement")
    commande_existante = Commande.objects.filter(
        panier=panier,
        statut__in=['validee', 'payee', 'livraison', 'terminee']
    ).first()
    
    if commande_existante:
        messages.info(request, f"ℹ️ Une commande est déjà en cours ({commande_existante.get_statut_display()}).")
        return redirect('order_app:detail-commande', commande_existante.pk)
    
    # ✅ Créer une nouvelle commande
    commande, _ = Commande.objects.get_or_create(
        panier=panier,
    )
   
    commande.statut = 'validee'
    commande.save()
    
    messages.success(request, "✅ Commande validée avec succès !")
    return redirect('order_app:detail-commande', commande.pk)

@login_required
def annuler_commande(request, commande_id):
    """Annule une commande en cours"""
    commande = get_object_or_404(Commande, id=commande_id, panier__client=request.user)
    
    if commande.statut in ["payee", "livraison", "terminee"]:
        messages.error(request, "❌ Cette commande ne peut pas être annulée.")
        return redirect('order_app:detail-commande', commande.pk)
    
    commande.statut = 'annulee'
    commande.save()
    
    messages.success(request, "✅ Commande annulée avec succès !")
    return redirect('order_app:panier')

class CommandDetailView(LoginRequiredMixin, UserPassesTestMixin ,DetailView):
    def test_func(self):
        return self.request.user.role == "client"
    
    model = Commande
    template_name = "order_templates/commande_detail.html" 
    context_object_name = "commande"
    
    def get_queryset(self):
       return Commande.objects.filter(panier__client=self.request.user)
    
    
    



# ============================================================
# 1. Voir le panier (GET)
# ============================================================

class PanierDetailView(APIView):
    """Retourne le panier complet du user connecté
          GET /api/order/panier/
    """
    permission_classes = [IsAuthenticated] # Seulement les clients connectés
    
    def get(self, request):
        #on récupère ou on cree le panier
        panier, created = Panier.objects.get_or_create(client=request.user)
        
        #serialise le panier(convertit en json)
        serializer = PanierSerializer(panier)

        #retourne la reponse avec le panier(convertit en JSON)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AjouterPanierView(APIView):
    """Ajoute un produit au panier ,
        Augmente la quantité si le produit exite déja 
    """
    permission_classes = [IsAuthenticated] 
    
    def post(self, request):
        product_id = request.data.get('product_id')
        quantite = request.data.get("quantite", 1)
        
        # Vérifie que le produit existe
        product = get_object_or_404(Products, id=product_id)
        
        #recupère le panier ou le cree
        panier, created = Panier.objects.get_or_create(client=request.user)
        
        #Vérifie si l'article est déja dans le panier
        article, created= ArticlePanier.objects.get_or_create(panier=panier,
                                                              products=product,
                                                              defaults={'quantite': quantite})
        
        # Si l'article existait déjà, on augmente la quantité
        if not created:
            article.quantite += quantite
            article.save()
        
        # Retourne le panier mis à jour
        serializer = PanierSerializer(panier)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================================
# 3. Modifier la quantité d'un article (PUT)
# ============================================================
class ModifierArticlePanierView(APIView):
    """ 
    Modifier la quantité d'un article dans le panier
    PUT /api/order/panier/modifier/<article_id>/
    body: {"quantite":5}
    """
    permission_classes = [IsAuthenticated]
    
    def put(self, request, article_id):
        # Récupère l'article (en vérifiant qu'il appartient au client connecté)
        article = get_object_or_404(
            ArticlePanier,
            id=article_id,
            panier__client = request.user
        )
        
        # Récupère la nouvelle quantité
        quantite = request.data.get("quantite")
    
        if quantite is not None and int(quantite) > 0:
            # Mise à jour de la quantité
            article.quantite = int(quantite)
            article.save()
        else:
            # Si quantité = 0, on supprime l'article
            article.delete()
            
        # Retourne le panier mis à jour
        panier = article.panier if quantite > 0 else Panier.objects.get(client=request.user)
        serializer = PanierSerializer(panier)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ============================================================
# 4. Supprimer un article du panier (DELETE)
# ============================================================

class RetirerArticlePAnierView(APIView):
    """
    Supprime un article spécifique du panier.
    DELETE /api/order/panier/retirer/<article_id>/
    """
    def delete(self, request, article_id):
        # Récupère l'article (en vérifiant qu'il appartient au client)
        article = get_object_or_404(
            ArticlePanier,
            id=article_id,
            panier__client=request.user
        )
        
        #Supprime l'article
        panier = article.panier
        article.delete()
        
        # Retourne le panier mis à jour
        serializer = PanierSerializer(panier)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ============================================================
# 5. Vider tout le panier (DELETE)
# ============================================================
class ViderPanierView(APIView):
    """
    Supprime tous les articles du panier.
    DELETE /api/order/panier/vider/
    """
    
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        # Récupère le panier du client
        panier, created = Panier.objects.get_or_create(client=request.user)
        
        if not panier.articles.exists():
            # Supprime tous les articles
            panier.articles.all().delete()
        else:
            return Response({"info":"Votre panier ne contient pas d'article"}, status=status.HTTP_404_NOT_FOUND)
            
        # Retourne un statut 204 (No Content)
        return Response(status=status.HTTP_204_NO_CONTENT)
        
        
    

# ============================================================
# 1. Valider une commande (POST)
# ============================================================ 

class ValiderCommandeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        panier , created = Panier.objects.get_or_create(client=request.user) 
        
        if panier.articles.count()== 0:
            return Response({"error":"Panier vide"}, status=status.HTTP_400_BAD_REQUEST)   
        
        commande = Commande.objects.get_or_create(panier=panier, statut="Chargement")
        serializer = CommandeSerializer(commande)
        return Response(serializer.data, status=status.HTTP_201_CREATED)   
        