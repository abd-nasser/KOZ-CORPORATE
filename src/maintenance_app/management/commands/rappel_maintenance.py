from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from client_app.models import Maintenance  # Ajustez selon le nom exact de votre app


class Command(BaseCommand):
    help = 'Envoie un e-mail de rappel HTML pour les maintenances prévues dans 7 jours (J-7)'

    def handle(self, *args, **kwargs):
        date_limite = timezone.now().date() + timedelta(days=7)
        
        maintenances = Maintenance.objects.filter(
            date_prochaine=date_limite,
            statut='planifiee',
            rappel_envoye=False
        ).select_related('client')

        if not maintenances.exists():
            self.stdout.write(self.style.WARNING("Aucune maintenance J-7 à notifier aujourd'hui."))
            return

        site_url = getattr(settings, 'SITE_URL', 'https://koz-corporate.pro')
        succes_count = 0
        erreur_count = 0

        for m in maintenances:
            if not m.client or not m.client.email:
                self.stdout.write(
                    self.style.WARNING(f"Echec : Pas d'e-mail pour le dossier Maintenance #{m.id}")
                )
                continue

            # Construction du lien vers la fiche maintenance
            lien_maintenance = f"{site_url}{m.get_absolute_url()}" if hasattr(m, 'get_absolute_url') else ""

            context_email = {
                'client': m.client,
                'maintenance': m,
                'lien_maintenance': lien_maintenance,
            }

            try:
                html_message = render_to_string('emails/maintenance/rappel_maintenance_j7.html', context_email)
                plain_message = strip_tags(html_message)

                send_mail(
                    subject="🔧 Rappel : votre maintenance approche (J-7) - KOZ Services",
                    message=plain_message,
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
                    recipient_list=[m.client.email],
                    fail_silently=False,
                )

                m.rappel_envoye = True
                m.save(update_fields=['rappel_envoye'])

                succes_count += 1
                self.stdout.write(self.style.SUCCESS(f"✔ Rappel J-7 envoyé à {m.client.email} (Dossier #{m.id})"))

            except Exception as e:
                erreur_count += 1
                self.stdout.write(
                    self.style.ERROR(f"❌ Erreur lors de l'envoi à {m.client.email} (Dossier #{m.id}) : {str(e)}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"\nTerminé : {succes_count} rappel(s) envoyé(s), {erreur_count} erreur(s).")
        )