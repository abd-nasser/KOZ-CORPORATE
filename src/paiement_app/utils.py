from auth_app.models import kozUser
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse_lazy, reverse
import logging
logger = logging.getLogger(__name__)

def notifier_stock_faible(produit):
    try:
        commerciaux = kozUser.objects.filter(role="commercial")
        emails = [c.email for c in commerciaux if c.email]
        if not emails:
            return

        context_email = {
            'produit': produit.nom,
            'stock_restant': produit.stock,
            'lien_produit': settings.SITE_URL + reverse('products_app:product-detail', kwargs={'pk': produit.pk}),
        }
        html_message = render_to_string('emails/stock/stock_faible.html', context_email)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=f"⚠️ Stock faible : {produit.nom} ({produit.stock} restant)",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails,
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Erreur notification stock faible pour {produit.nom}: {e}")