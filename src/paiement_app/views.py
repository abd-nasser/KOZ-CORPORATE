from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse
import requests
import json
import logging
from django.db.models import F
from django.db import transaction
from products_app.models import Products
from order_app.models import Commande
from .models import Paiement
from .utils import notifier_stock_faible

logger = logging.getLogger(__name__)


@login_required
def page_paiement(request, commande_id):
    """
    Affiche la page de paiement pour une commande
    """
    # ✅ Vérifier que la commande existe et appartient au client
    commande = get_object_or_404(
        Commande,
        id=commande_id,
        panier__client=request.user
    )
    
    # ✅ Vérifier que la commande est en état "Chargement"
    if commande.statut != "validee":
        messages.warning(request, f"Cette commande est déjà {commande.get_statut_display()}.")
        return redirect('order_app:detail-commande', commande.pk)
    
    # ✅ Vérifier que le panier n'est pas vide
    if not commande.panier.articles.exists():
        messages.error(request, "Votre panier est vide.")
        return redirect('order_app:panier')
    
    context = {
        'commande': commande,
        'total': commande.panier.total_panier(),
        'montant_ttc': commande.panier.total_panier() ,  # TVA 18%
    }
    
    return render(request, 'paiement_templates/paiement.html', context)


@login_required
def initier_paiement(request, commande_id):
    """
    Initie le paiement via LigdiCash (Orange Money)
    """
    commande = get_object_or_404(
        Commande,
        id=commande_id,
        panier__client=request.user
    )
    
    if request.method != 'POST':
        return redirect('paiement_app:page-paiement', commande_id=commande.id)
    
    # ✅ Récupérer les données du formulaire
    telephone = request.POST.get('telephone', '').replace(' ', '')
    otp = request.POST.get('otp', '')
    montant = int(commande.panier.total_panier())
    
    # ✅ Validation de base
    if not telephone or not otp:
        return JsonResponse({
            'success': False,
            'error': 'Veuillez remplir tous les champs.'
        })
    
    if len(telephone) != 8 or not telephone.isdigit():
        return JsonResponse({
            'success': False,
            'error': 'Numéro de téléphone invalide (8 chiffres requis).'
        })
    
    if len(otp) != 6 or not otp.isdigit():
        return JsonResponse({
            'success': False,
            'error': 'OTP invalide (6 chiffres requis).'
        })
    
    # ✅ Construire le numéro complet (+226)
    numero_complet = f"226{telephone}"
    
    # ✅ Construire le payload LigdiCash
    payload = {
        "commande": {
            "invoice": {
                "total_amount": montant,
                "devise": "XOF",
                "description": f"Commande KOZ #{commande.id}",
                "customer": numero_complet,
                "customer_firstname": request.user.nom_complet.split()[0] if request.user.nom_complet else "Client",
                "customer_lastname": request.user.nom_complet.split()[-1] if request.user.nom_complet else "KOZ",
                "customer_email": request.user.email,
                "otp": otp
            },
            "store": {
                "name": "KOZ Services",
                "website_url": "https://www.koz-corporate.pro"
            },
            "actions": {
                "callback_url": request.build_absolute_uri(
                    reverse('paiement_app:callback-ligdicash')
                )
            },
            "custom_data": {
                "commande_id": commande.id,
                "client_id": request.user.id
            }
        }
    }
    
    # ✅ Envoyer la requête à LigdiCash
    try:
        response = requests.post(
            "https://app.ligdicash.com/pay/v01/straight/checkout-invoice/create",
            headers={
                "Apikey": settings.LIGDICASH_API_KEY,
                "Authorization": f"Bearer {settings.LIGDICASH_API_TOKEN}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30
        )
        
        data = response.json()
        logger.info(f"LigdiCash response: {data}")
        
        if response.status_code == 200 and data.get('response_code') == '00':
            with transaction.atomic():
                # ✅ Créer la transaction en base
                paiement = Paiement.objects.create(
                    commande=commande,
                    client=request.user,
                    montant=montant,
                    token=data.get('token'),
                    statut='en_attente'
                )

                articles_panier = commande.panier.articles.all()

                # ✅ Vérification du stock AVANT décrémentation
                stock_insuffisant = []
                for ligne in articles_panier:
                    if ligne.products.stock < ligne.quantite:
                        stock_insuffisant.append(ligne.products.nom)

                if stock_insuffisant:
                    logger.error(
                        f"Stock insuffisant pour paiement {paiement.id} : {', '.join(stock_insuffisant)}"
                    )
                    messages.error(request,  f"Stock insuffisant pour paiement {paiement.id} : {', '.join(stock_insuffisant)}" )
                    # à toi de décider la suite : annuler le paiement ? notifier le client/commercial ?
                    # pour l'instant on ne décrémente rien et on ne casse pas le flux de paiement déjà validé côté prestataire

                else:
                    
                    # ✅ Décrémentation atomique du stock, vi
                    # a F() pour éviter les race conditions
                    produit_a_verifier = []
                    for ligne in articles_panier:
                        Products.objects.filter(id=ligne.products_id).update(
                            stock=F('stock') - ligne.quantite
                        )
                        produit_a_verifier.append(ligne.products_id)
                    
                    # ✅ Alerte stock faible — après décrémentation, avec la valeur fraîche
                    produits_stock_faible = Products.objects.filter(
                        id__in=produit_a_verifier,
                        stock__lte=5
                    )
                    for produit in produits_stock_faible:
                        notifier_stock_faible(produit)
                        
                   
                        
                    return JsonResponse({
                        'success': True,
                        'message': 'Paiement initié avec succès',
                        'token': data.get('token'),
                        'paiement_id': paiement.id,
                    })
        else:
            # ❌ Erreur LigdiCash
            return JsonResponse({
                'success': False,
                'error': data.get('response_text', 'Erreur inconnue')
            })
            
    except requests.exceptions.Timeout:
        return JsonResponse({
            'success': False,
            'error': 'Le paiement a expiré. Veuillez réessayer.'
        })
    except Exception as e:
        logger.error(f"Erreur paiement: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Une erreur est survenue. Veuillez réessayer.'
        })


@login_required
def confirmation_paiement(request):
    """
    Page de confirmation après paiement
    """
    # Récupérer la dernière commande du client
    commande = Commande.objects.filter(
        panier__client=request.user
    ).order_by('-date_commande').first()
    
    if not commande:
        return redirect('order_app:panier')
    
    context = {
        'commande': commande,
        'paiement': commande.paiements if hasattr(commande, 'paiements') else None,
    }
    
    return render(request, 'paiement_templates/confirmation.html', context)




def callback_ligdicash(request):
    """
    Webhook reçu de LigdiCash pour confirmer le paiement
    """
    try:
        payload = json.loads(request.body)
        logger.info(f"Callback LigdiCash reçu: {payload}")
        
        token = payload.get('token')
        statut = payload.get('status')
        transaction_id = payload.get('transaction_id')
        montant = payload.get('amount')
        
        if not token:
            logger.error("Callback sans token")
            return JsonResponse({"error": "Token manquant"}, status=400)
        
        # ✅ Récupérer le paiement
        paiement = get_object_or_404(Paiement, token=token)
        
        # ✅ Vérifier le montant
        if montant and int(montant) != paiement.montant:
            logger.error(f"Montant incohérent: {montant} vs {paiement.montant}")
            return JsonResponse({"error": "Montant incohérent"}, status=400)
        
        # ✅ Mettre à jour le paiement
        if statut == 'success':
            paiement.statut = 'paye'
            paiement.transaction_id = transaction_id
            paiement.save()
            
            # ✅ Mettre à jour la commande
            commande = paiement.commande
            commande.statut = 'payee'
            commande.save()
            
            logger.info(f"✅ Paiement {paiement.id} confirmé pour commande {commande.id}")
            
            return JsonResponse({
                "status": "ok",
                "message": "Paiement confirmé"
            }, status=200)
        else:
            paiement.statut = 'echoue'
            paiement.save()
            
            logger.warning(f"❌ Paiement {paiement.id} échoué")
            
            return JsonResponse({
                "status": "failed",
                "message": "Paiement échoué"
            }, status=200)
            
    except json.JSONDecodeError:
        logger.error("Payload JSON invalide")
        return JsonResponse({"error": "JSON invalide"}, status=400)
    except Exception as e:
        logger.error(f"Erreur callback: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)



