import hashlib
import json
import logging
import uuid
from decimal import Decimal, InvalidOperation

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from order_app.models import Commande
from products_app.models import Products
from .models import Paiement
from .utils import notifier_stock_faible


logger = logging.getLogger(__name__)
LIGDICASH_API_URL = "https://app.ligdicash.com/pay"


def _ligdicash_headers(include_content_type=False):
    """Construit les en-têtes authentifiés requis par l'API LigdiCash."""
    api_key = settings.LIGDICASH_API_KEY
    api_token = settings.LIGDICASH_API_TOKEN
    if not api_key or not api_token:
        logger.error("Les identifiants API LigdiCash ne sont pas configurés.")
        return None

    headers = {
        "Apikey": api_key,
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
    }
    if include_content_type:
        headers["Content-Type"] = "application/json"
    return headers


def _commande_payable(request, commande_id):
    """Charge une commande appartenant au client et vérifie qu'elle est payable."""
    commande = get_object_or_404(
        Commande,
        id=commande_id,
        panier__client=request.user,
    )
    if commande.statut != "validee":
        return None, JsonResponse(
            {"success": False, "error": "Cette commande ne peut pas être payée."},
            status=400,
        )
    if not commande.panier.articles.exists():
        return None, JsonResponse(
            {"success": False, "error": "Votre panier est vide."},
            status=400,
        )
    return commande, None


def _telephone_burkina(request):
    """Valide le numéro local à 8 chiffres et ajoute l'indicatif Burkina Faso."""
    telephone = "".join(request.POST.get("telephone", "").split())
    if len(telephone) != 8 or not telephone.isdigit():
        return None
    return f"226{telephone}"


def _montant_commande(commande):
    """Convertit le total en montant XOF entier ou renvoie None s'il est invalide."""
    try:
        montant = Decimal(str(commande.panier.total_panier()))
    except (InvalidOperation, TypeError, ValueError):
        return None
    if not montant.is_finite() or montant != montant.to_integral_value():
        return None
    return int(montant)


@login_required
def page_paiement(request, commande_id):
    """Affiche le formulaire LigdiCash d'une commande encore payable."""
    commande = get_object_or_404(
        Commande,
        id=commande_id,
        panier__client=request.user,
    )
    if commande.statut != "validee":
        messages.warning(request, f"Cette commande est déjà {commande.get_statut_display()}.")
        return redirect("order_app:detail-commande", commande.pk)
    if not commande.panier.articles.exists():
        messages.error(request, "Votre panier est vide.")
        return redirect("order_app:panier")

    context = {
        "commande": commande,
        "total": commande.panier.total_panier(),
        "montant_ttc": commande.panier.total_panier(),
    }
    return render(request, "paiement_templates/paiement.html", context)


@login_required
@require_POST
def envoyer_otp(request, commande_id):
    """Demande à LigdiCash d'envoyer un OTP et lie la demande au téléphone et au montant dans la session."""
    commande, error_response = _commande_payable(request, commande_id)
    if error_response:
        return error_response

    telephone = _telephone_burkina(request)
    if not telephone:
        return JsonResponse({
            "success": False,
            "error": "Numéro de téléphone invalide (8 chiffres requis).",
        }, status=400)

    montant = _montant_commande(commande)
    if montant is None:
        return JsonResponse({
            "success": False,
            "error": "Le montant de la commande est invalide.",
        }, status=400)
    if montant < 10 or montant > 2_000_000:
        return JsonResponse({
            "success": False,
            "error": "Le montant doit être compris entre 10 et 2 000 000 FCFA.",
        }, status=400)
    if Paiement.objects.filter(commande=commande, statut="en_attente").exists():
        return JsonResponse({
            "success": False,
            "error": "Un paiement est déjà en cours pour cette commande.",
        }, status=409)

    headers = _ligdicash_headers()
    if not headers:
        return JsonResponse({
            "success": False,
            "error": "Le service de paiement est momentanément indisponible.",
        }, status=503)

    try:
        response = requests.get(
            f"{LIGDICASH_API_URL}/v02/debitotp/{telephone}/{montant}",
            headers=headers,
            timeout=30,
        )
        data = response.json()
    except requests.exceptions.RequestException:
        logger.exception("Erreur réseau lors de la demande d'OTP LigdiCash.")
        return JsonResponse({
            "success": False,
            "error": "Impossible de contacter LigdiCash. Veuillez réessayer.",
        }, status=502)
    except ValueError:
        logger.error("Réponse JSON invalide reçue pendant la demande d'OTP LigdiCash.")
        return JsonResponse({
            "success": False,
            "error": "Réponse invalide du service de paiement.",
        }, status=502)

    if not isinstance(data, dict):
        return JsonResponse({
            "success": False,
            "error": "Réponse invalide du service de paiement.",
        }, status=502)
    if not response.ok or data.get("error") is not False:
        logger.warning(
            "LigdiCash a refusé la demande d'OTP pour la commande %s (HTTP %s).",
            commande.id,
            response.status_code,
        )
        return JsonResponse({
            "success": False,
            "error": data.get("message", "LigdiCash n'a pas pu envoyer le code OTP."),
        }, status=400)

    request.session[f"ligdicash_otp_{commande.id}"] = {
        "telephone_hash": hashlib.sha256(telephone.encode()).hexdigest(),
        "montant": montant,
    }
    return JsonResponse({
        "success": True,
        "message": "Code OTP envoyé. Vérifiez vos SMS ou votre application LigdiCash.",
    })


@login_required
@require_POST
def initier_paiement(request, commande_id):
    """Soumet l'OTP au wallet LigdiCash, puis enregistre le token et la référence de transaction."""
    commande, error_response = _commande_payable(request, commande_id)
    if error_response:
        return error_response

    telephone = _telephone_burkina(request)
    otp = request.POST.get("otp", "").strip()
    montant = _montant_commande(commande)
    session_key = f"ligdicash_otp_{commande.id}"
    otp_request = request.session.get(session_key)

    if not telephone or not otp or not otp.isdigit() or len(otp) != 6:
        return JsonResponse({
            "success": False,
            "error": "Vérifiez le numéro de téléphone et le code OTP à 6 chiffres.",
        }, status=400)
    if montant is None:
        return JsonResponse({
            "success": False,
            "error": "Le montant de la commande est invalide.",
        }, status=400)
    if otp_request != {
        "telephone_hash": hashlib.sha256(telephone.encode()).hexdigest(),
        "montant": montant,
    }:
        return JsonResponse({
            "success": False,
            "error": "Demandez un nouveau code OTP avant de confirmer le paiement.",
        }, status=400)
    if montant < 10 or montant > 2_000_000:
        return JsonResponse({
            "success": False,
            "error": "Le montant doit être compris entre 10 et 2 000 000 FCFA.",
        }, status=400)
    if Paiement.objects.filter(commande=commande, statut="en_attente").exists():
        return JsonResponse({
            "success": False,
            "error": "Un paiement est déjà en cours pour cette commande.",
        }, status=409)

    headers = _ligdicash_headers(include_content_type=True)
    if not headers:
        return JsonResponse({
            "success": False,
            "error": "Le service de paiement est momentanément indisponible.",
        }, status=503)

    transaction_id = uuid.uuid4().hex
    payload = {
        "commande": {
            "invoice": {
                "items": [
                    {
                        "name": ligne.products.nom,
                        "description": ligne.products.description_courte or "",
                        "quantity": ligne.quantite,
                        "unit_price": int(ligne.products.prix_actuel),
                        "total_price": int(ligne.sous_total()),
                    }
                    for ligne in commande.panier.articles.select_related("products").all()
                ],
                "total_amount": montant,
                "devise": "XOF",
                "description": f"Commande KOZ #{commande.id}",
                "customer": telephone,
                "customer_firstname": request.user.nom_complet.split()[0] if request.user.nom_complet else "Client",
                "customer_lastname": request.user.nom_complet.split()[-1] if request.user.nom_complet else "KOZ",
                "customer_email": request.user.email,
                "otp": otp,
            },
            "store": {
                "name": "KOZ Services",
                "website_url": "https://www.koz-corporate.pro",
            },
            "actions": {
                "callback_url": request.build_absolute_uri(
                    reverse("paiement_app:callback-ligdicash")
                ),
            },
            "custom_data": {
                "transaction_id": transaction_id,
            },
        },
    }

    try:
        response = requests.post(
            f"{LIGDICASH_API_URL}/v02/debitwallet/withotp",
            headers=headers,
            json=payload,
            timeout=30,
        )
        data = response.json()
    except requests.exceptions.RequestException:
        logger.exception("Erreur réseau pendant la validation du paiement LigdiCash.")
        return JsonResponse({
            "success": False,
            "error": "Impossible de contacter LigdiCash. Veuillez réessayer.",
        }, status=502)
    except ValueError:
        logger.error("Réponse JSON invalide reçue pendant la validation du paiement.")
        return JsonResponse({
            "success": False,
            "error": "Réponse invalide du service de paiement.",
        }, status=502)

    if not isinstance(data, dict):
        return JsonResponse({
            "success": False,
            "error": "Réponse invalide du service de paiement.",
        }, status=502)
    token = data.get("token")
    if not response.ok or data.get("response_code") != "00" or not token:
        logger.warning(
            "LigdiCash a refusé le paiement de la commande %s (HTTP %s, code %s).",
            commande.id,
            response.status_code,
            data.get("response_code"),
        )
        return JsonResponse({
            "success": False,
            "error": data.get("response_text", "LigdiCash n'a pas pu valider le paiement."),
        }, status=400)

    with transaction.atomic():
        paiement = Paiement.objects.create(
            commande=commande,
            methode="mobile_ligdicash",
            montant=montant,
            token=token,
            statut="en_attente",
            ligdicash_phone=telephone,
            ligdicash_transaction_id=transaction_id,
        )
        commande.paiements = paiement
        commande.save(update_fields=["paiements"])
    request.session.pop(session_key, None)

    return JsonResponse({
        "success": True,
        "message": "Paiement envoyé. Sa confirmation peut prendre quelques instants.",
        "paiement_id": paiement.id,
    })


@login_required
def confirmation_paiement(request):
    """Affiche la page de confirmation liée à la dernière commande du client."""
    commande = Commande.objects.filter(
        panier__client=request.user
    ).order_by("-date_commande").first()
    if not commande:
        return redirect("order_app:panier")

    return render(request, "paiement_templates/confirmation.html", {
        "commande": commande,
        "paiement": commande.paiements if hasattr(commande, "paiements") else None,
    })


@require_POST
def callback_ligdicash(request):
    """Traite un callback POST LigdiCash sans lui faire confiance comme preuve de paiement.

    Étapes :
    1. Décode le corps JSON reçu et lit ``transaction_id`` dans
       ``custom_data`` pour retrouver le paiement enregistré par le site.
    2. Si le paiement est déjà final (payé, échoué ou annulé), ne refait
       aucune opération et renvoie son statut avec HTTP 200.
    3. Appelle l'API LigdiCash ``confirm`` avec le token sauvegardé par le
       site, puis utilise uniquement le statut et le montant de cette réponse.
    4. Si le paiement est confirmé et que le montant correspond, verrouille
       le paiement et les produits, diminue le stock une seule fois, envoie
       les alertes de stock faible, puis marque paiement et commande payés.

    Réponses retournées :
    - HTTP 400 si le JSON est invalide, si ``transaction_id`` manque ou si
      le montant confirmé diffère du montant enregistré.
    - HTTP 404 si la référence reçue ne correspond à aucun paiement connu.
    - HTTP 503 si les identifiants API manquent ou si LigdiCash est
      injoignable pendant la vérification.
    - HTTP 502 si la réponse de confirmation est invalide, si LigdiCash
      signale une erreur API, si le montant est illisible ou si le statut
      reçu n'est ni ``pending``, ``notcompleted`` ni ``completed``.
    - HTTP 200 avec ``status: pending`` si LigdiCash n'a pas encore terminé
      le paiement; l'enregistrement reste en attente.
    - HTTP 200 avec ``status: echec`` si LigdiCash confirme que le paiement
      n'a pas abouti; le paiement est marqué échoué.
    - HTTP 200 avec le statut final enregistré si le callback est un doublon.
    - HTTP 200 avec ``status: paye`` après traitement d'un paiement confirmé.

    Si le paiement est confirmé mais le stock est insuffisant, l'incident est
    journalisé; le code actuel marque quand même le paiement et la commande
    comme payés, mais ne diminue pas le stock et ne lance pas de remboursement.
    """
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        logger.error("Payload JSON invalide dans le callback LigdiCash.")
        return JsonResponse({"error": "JSON invalide"}, status=400)

    custom_data = payload.get("custom_data", [])
    transaction_id = None
    if isinstance(custom_data, list):
        transaction_id = next(
            (
                item.get("valueof_customdata")
                for item in custom_data
                if isinstance(item, dict)
                and item.get("keyof_customdata") == "transaction_id"
            ),
            None,
        )
    if not isinstance(transaction_id, str) or not transaction_id:
        logger.warning("Callback LigdiCash sans transaction_id exploitable.")
        return JsonResponse({"error": "transaction_id manquant"}, status=400)

    paiement = (
        Paiement.objects.select_related("commande", "commande__panier")
        .filter(ligdicash_transaction_id=transaction_id)
        .first()
    )
    if not paiement:
        logger.warning("Callback LigdiCash pour une transaction inconnue.")
        return JsonResponse({"error": "Transaction inconnue"}, status=404)
    if paiement.statut in ("paye", "echec", "annule"):
        return JsonResponse({"status": paiement.statut}, status=200)

    headers = _ligdicash_headers()
    if not headers:
        return JsonResponse({"error": "Service de paiement indisponible"}, status=503)

    try:
        response = requests.get(
            f"{LIGDICASH_API_URL}/v01/redirect/checkout-invoice/confirm/",
            params={"invoiceToken": paiement.token},
            headers=headers,
            timeout=30,
        )
        data = response.json()
    except requests.exceptions.RequestException:
        logger.exception("Erreur réseau pendant la confirmation LigdiCash.")
        return JsonResponse({"error": "Confirmation LigdiCash indisponible"}, status=503)
    except ValueError:
        logger.error("Réponse JSON invalide reçue pendant la confirmation LigdiCash.")
        return JsonResponse({"error": "Réponse LigdiCash invalide"}, status=502)

    if not isinstance(data, dict):
        return JsonResponse({"error": "Réponse LigdiCash invalide"}, status=502)
    if not response.ok or data.get("response_code") != "00":
        logger.error(
            "Échec de vérification LigdiCash pour le paiement %s (HTTP %s, code %s).",
            paiement.id,
            response.status_code,
            data.get("response_code"),
        )
        return JsonResponse({"error": "Vérification LigdiCash échouée"}, status=502)

    statut = data.get("status")
    if statut == "pending":
        return JsonResponse({"status": "pending"}, status=200)
    if statut == "notcompleted":
        paiement.statut = "echec"
        paiement.save(update_fields=["statut"])
        return JsonResponse({"status": "echec"}, status=200)
    if statut != "completed":
        logger.error("Statut LigdiCash inconnu pour le paiement %s.", paiement.id)
        return JsonResponse({"error": "Statut LigdiCash invalide"}, status=502)

    try:
        montant_confirme = Decimal(str(data.get("amount", data.get("montant"))))
    except (InvalidOperation, TypeError, ValueError):
        logger.error("Montant invalide dans confirm pour le paiement %s.", paiement.id)
        return JsonResponse({"error": "Montant LigdiCash invalide"}, status=502)
    if not montant_confirme.is_finite() or montant_confirme != paiement.montant:
        logger.error("Montant LigdiCash incohérent pour le paiement %s.", paiement.id)
        return JsonResponse({"error": "Montant incohérent"}, status=400)

    with transaction.atomic():
        paiement = Paiement.objects.select_for_update().select_related(
            "commande", "commande__panier"
        ).get(pk=paiement.pk)
        if paiement.statut != "en_attente":
            return JsonResponse({"status": paiement.statut}, status=200)

        articles_panier = list(
            paiement.commande.panier.articles.select_related("products").all()
        )
        produit_ids = {ligne.products_id for ligne in articles_panier}
        produits = {
            produit.id: produit
            for produit in Products.objects.select_for_update().filter(id__in=produit_ids)
        }
        stock_insuffisant = [
            ligne.products.nom
            for ligne in articles_panier
            if ligne.products_id not in produits
            or produits[ligne.products_id].stock < ligne.quantite
        ]
        if stock_insuffisant:
            logger.error(
                "Paiement %s confirmé mais stock insuffisant pour : %s",
                paiement.id,
                ", ".join(stock_insuffisant),
            )
        else:
            for ligne in articles_panier:
                Products.objects.filter(id=ligne.products_id).update(
                    stock=F("stock") - ligne.quantite
                )
            produits_stock_faible = Products.objects.filter(
                id__in=produit_ids,
                stock__lte=3,
            )
            for produit in produits_stock_faible:
                notifier_stock_faible(produit)

        paiement.statut = "paye"
        paiement.save(update_fields=["statut"])
        paiement.commande.statut = "payee"
        paiement.commande.save(update_fields=["statut"])

    return JsonResponse({"status": "paye", "message": "Paiement confirmé"}, status=200)
