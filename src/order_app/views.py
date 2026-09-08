from django.db import transaction
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Panier, ArticlePanier, Commande
from products_app.models import Products, CategorieProducts
from .serializers import PanierSerializer, ArticlePanierSerializer, CommandeSerializer

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Sum
from .models import Commande
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

class CommandDetailView(LoginRequiredMixin, DetailView):
    """Affiche les détails d'une commande spécifique"""
    
    model = Commande
    template_name = "order_templates/commande_detail.html" 
    context_object_name = "commande"
   
    def get_queryset(self):
        if self.request.user.role == "client":
            return Commande.objects.filter(panier__client=self.request.user)
        else:
            return Commande.objects.all()    
            
  
   


class CommandeListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Commande
    template_name = "order_templates/commande_list.html"
    context_object_name = "commandes"

    def test_func(self):
        return self.request.user.role in ["commercial", "directeur"]

    def get_queryset(self):
        # Récupération de toutes les commandes pour la direction/commercial
        queryset = Commande.objects.select_related('panier__client').order_by('-date_commande')

        # 1. Filtre Recherche Texte (HTMX)
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(id__icontains=query) |
                Q(panier__client__nom_complet__icontains=query) |
                
                Q(panier__client__telephone__icontains=query)
            )

        # 2. Filtre par Statut (HTMX)
        statut = self.request.GET.get('statut', 'all')
        if statut and statut != 'all':
            queryset = queryset.filter(statut=statut)

        return queryset

    def get_template_names(self):
        # Si c'est une requête HTMX, on renvoie seulement le tableau partiel
        if self.request.headers.get('HX-Request'):
            return ["partials/order/commande_table.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_cmds = Commande.objects.all()
        commandes_stats = all_cmds.select_related('panier').prefetch_related(
            'panier__articles__products'
        )
        
        # Conserver les filtres actifs dans le contexte
        context['statut_actif'] = self.request.GET.get('statut', 'all')
        context['search_q'] = self.request.GET.get('q', '')
        
        # Stats pour les cartes
        context['stats'] = {
            'total': all_cmds.count(),
            'en_attente': all_cmds.filter(statut__in=['chargement', 'validee']).count(),
            'terminees': all_cmds.filter(statut='terminee').count(),
            'ca_total': sum(
                commande.panier.total_panier()
                for commande in commandes_stats
                if commande.statut != 'annulee' and commande.statut != 'chargement'
            )
        }
        return context


from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from .models import Commande

class ChangerStatutCommandeView(LoginRequiredMixin, UserPassesTestMixin, View):
    
    def test_func(self):
        # Vérifie que l'utilisateur n'est pas un client
        return self.request.user.role != 'client'

    def post(self, request, pk):
        commande = get_object_or_404(Commande, pk=pk)
        nouveau_statut = request.POST.get('statut')
        
        # Liste des statuts autorisés
        statuts_valides = ['chargement', 'validee', 'payee', 'livraison', 'terminee', 'annulee']

        if nouveau_statut in statuts_valides:
            commande.statut = nouveau_statut
            commande.save()
            messages.success(request, f"Le statut de la commande #{commande.id} a été mis à jour.")
        else:
            messages.error(request, "Statut sélectionné invalide.")

        # Redirige vers la page courante (détail commande ou liste)
        return redirect(request.META.get('HTTP_REFERER', 'order_app:commande-list'))

@login_required
def envoi_localisation(request):
    """Reçoit la position GPS et crée/met à jour la commande en statut 'brouillon'."""
    if request.method != "POST":
        messages.error(request, "❌ Méthode non autorisée.")
        return redirect('order_app:panier')
    
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')
    
    if not latitude or not longitude:
        messages.error(request, "❌ Position GPS invalide.")
        return redirect('order_app:panier')

    panier = get_object_or_404(Panier, client=request.user)
    
    with transaction.atomic():
        # Corrected: cibler le modèle Commande avec un statut temporaire 'brouillon'
        commande, created = Commande.objects.get_or_create(
            panier=panier,
            statut='chargement',  # Utiliser un statut temporaire pour la commande en cours de création
            defaults={'latitude': latitude, 'longitude': longitude}
        )
        
        if not created:
            commande.latitude = latitude
            commande.longitude = longitude
            commande.save()

    messages.success(request, "✅ Position GPS enregistrée avec succès !")
    return redirect('order_app:panier')


@login_required
def valider_commande(request):
    """Passe la commande brouillon existante au statut 'validee'."""
    panier = get_object_or_404(Panier, client=request.user)
    
    if not panier.articles.exists():
        messages.error(request, "❌ Votre panier est vide.")
        return redirect('order_app:panier')
    
    # 1. Empêcher la re-validation si une commande est déjà en cours
    commande_existante = Commande.objects.filter(
        panier=panier,
        statut__in=['validee', 'payee', 'livraison', 'terminee']
    ).first()
    
    if commande_existante:
        messages.info(request, f"ℹ️ Une commande est déjà en cours ({commande_existante.get_statut_display()}).")
        return redirect('order_app:detail-commande', commande_existante.pk)
    
    # 2. Récupérer la commande brouillon créée lors de l'envoi de la localisation
    commande = Commande.objects.filter(panier=panier, statut='chargement').first()
    
    if not commande or not (commande.latitude and commande.longitude):
        messages.error(request, "❌ Veuillez renseigner votre localisation avant de valider la commande.")
        return redirect('order_app:panier')
    
    # 3. Validation finale de la commande
    commande.statut = 'validee'
    commande.save()
    
    messages.success(request, "✅ Commande validée avec succès !")
    return redirect('order_app:detail-commande', commande.pk)

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
        