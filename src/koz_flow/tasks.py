import logging
from celery import shared_task
from django.core.mail import send_mail as django_send_mail

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, subject,  plain_message, from_email, recipient_list, html_message=None):
    try:
        django_send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False
        )
    except Exception as exc:
        logger.error(f"Échec envoi email à {recipient_list}: {exc}")
        raise self.retry(exc=exc)