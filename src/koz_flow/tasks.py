import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail as django_send_mail

# Initialisation du logger
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, subject, plain_message, from_email, recipient_list, html_message=None):
    # Sécurité si from_email est vide ou None
    from_email = from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', getattr(settings, 'EMAIL_HOST_USER', None))

    try:
        logger.info(f"[Celery] Début d'envoi d'email à {recipient_list} - Sujet: {subject}")

        django_send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False
        )

        logger.info(f"[Celery] Email envoyé avec succès à {recipient_list}")
        return f"Email envoyé à {recipient_list}"

    except Exception as exc:
        logger.error(f"[Celery] Échec envoi email à {recipient_list} : {exc}", exc_info=True)
        raise self.retry(exc=exc)
    
    

# commercial_app/tasks.py (ou l'emplacement de vos tâches)
import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage

from utils.pdf import render_to_pdf  # Adaptez l'import selon votre projet

logger = logging.getLogger(__name__)



@shared_task
def send_receipt_email_task(vente_id, numero_echeance):
    """
    Tâche Celery pour générer le reçu PDF et l'envoyer par email au client.
    """
    # 💡 L'import interne évite l'erreur AppRegistryNotReady au démarrage de Django/Celery
    from leads_app.models import PaiementFinancement

    try:
        # Récupération du paiement via l'ID de la vente et la référence
        paiement = PaiementFinancement.objects.select_related("vente__client").filter(
            vente_id=vente_id,
            reference=f"PAY-{vente_id}-{numero_echeance}"
        ).first()

        if not paiement:
            logger.error(f"Paiement introuvable pour Vente #{vente_id} et Échéance #{numero_echeance}")
            return

        vente = paiement.vente
        client = vente.client

        if not client or not client.email:
            logger.warning(f"Impossible d'envoyer le reçu : le client lié à la vente #{vente_id} n'a pas d'email.")
            return

        # 1. Génération du PDF en arrière-plan
        pdf_bytes = render_to_pdf('pdf/recu_paiement.html', {
            'paiement': paiement,
            'vente': vente
        })

        if not pdf_bytes:
            logger.error(f"Échec de la génération PDF pour le paiement #{paiement.id}")
            return

        # 2. Composition et envoi de l'email
        date_str = paiement.date_paiement.strftime('%d/%m/%Y') if paiement.date_paiement else ""
        sujet = f"Reçu de paiement - Échéance #{numero_echeance} ({paiement.reference})"
        corps = (
            f"Bonjour {client.nom_complet},\n\n"
            f"Nous vous confirmons le bon règlement de votre échéance de {paiement.montant} FCFA "
            f"effectué le {date_str}.\n\n"
            "Vous trouverez votre reçu officiel de paiement joint à ce message.\n\n"
            "Cordialement,\nL'équipe KOZ Services."
        )

        email = EmailMessage(
            subject=sujet,
            body=corps,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[client.email]
        )
        email.attach(f"Reçu_Paiement_{paiement.reference}.pdf", pdf_bytes, 'application/pdf')
        email.send(fail_silently=True)

    except Exception as e:
        logger.exception(f"Erreur lors de l'envoi du reçu par email pour la vente #{vente_id}: {e}")
        
        

import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


@shared_task
def send_document_modification_email_task(dossier_id, user_id, domain_url):
    """
    Tâche Celery pour envoyer l'email de notification de modification au client.
    """
    from django.contrib.auth import get_user_model
    from client_app.models import Documents

    User = get_user_model()

    try:
        dossier = Documents.objects.select_related("client", "demande_financement", "offre_financement").get(pk=dossier_id)
        user = User.objects.get(pk=user_id)

        demande = dossier.demande_financement
        offre = dossier.offre_financement

        if demande:
            contexte_nom = "demande de financement"
            vehicule = demande.Vehicul_interested if demande.Vehicul_interested else "Véhicule sélectionné"
        elif offre:
            contexte_nom = "offre de financement"
            vehicule = offre.vehicule_propose if offre.vehicule_propose else "Véhicule sélectionné"
        else:
            contexte_nom = "dossier"
            vehicule = "Non renseigné"

        chat_url = f"{domain_url}/chat/{dossier.client.pk}/"
        dossier_url = f"{domain_url}{reverse('leads_app:document-detail', kwargs={'pk': dossier.pk})}"

        context_email = {
            'client': dossier.client,
            'commercial': user,
            'dossier_id': dossier.id,
            'contexte': contexte_nom,
            'vehicule': vehicule,
            'lien_chat': chat_url,
            'lien_dossier': dossier_url,
        }

        html_message = render_to_string('emails/documents/demande_modification_documents.html', context_email)
        plain_message = strip_tags(html_message)

        send_mail(
            subject="📝 Demande de modification de vos documents - KOZ Services",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[dossier.client.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        logger.exception(f"Erreur lors de l'envoi de l'email pour le dossier #{dossier_id}: {e}")