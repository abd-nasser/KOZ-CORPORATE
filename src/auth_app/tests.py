# Importe le générateur Django pour créer exactement le même type de jeton que le parcours de production.
from django.contrib.auth.tokens import default_token_generator
# TestCase fournit client HTTP et base isolée; override_settings remplace SMTP par une boîte de test.
from django.test import TestCase, override_settings
# `reverse` construit les URL à partir de leurs noms sans recopier les chemins.
from django.urls import reverse
# Encode l'identifiant utilisateur dans le format attendu par l'URL de confirmation.
from django.utils.encoding import force_bytes
# Encode l'identifiant pour qu'il puisse être transporté dans une URL.
from django.utils.http import urlsafe_base64_encode

# Importe le modèle utilisateur personnalisé afin de créer le compte de test.
from .models import kozUser


# Active la boîte e-mail mémoire uniquement pendant cette classe de tests, sans contacter Gmail.
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
# Regroupe les vérifications du parcours de réinitialisation de mot de passe.
class PasswordResetTests(TestCase):
	# Crée un compte réel dans la base de test avant chaque scénario.
	def setUp(self):
		# Enregistre un utilisateur avec une adresse et un mot de passe connus du test.
		self.user = kozUser.objects.create_user(
			# L'adresse servira à vérifier le destinataire du courriel.
			email="client@example.com",
			# Le nom est requis par le gestionnaire utilisateur personnalisé.
			nom_complet="Client Test",
			# Le téléphone est requis par le gestionnaire utilisateur personnalisé.
			telephone="770000000",
			# Le mot de passe initial permet de vérifier ensuite que le changement a eu lieu.
			password="Original-Password-2026!",
		)

	# Vérifie qu'une adresse connue reçoit un lien Django de réinitialisation.
	def test_request_sends_reset_email_for_existing_account(self):
		# Envoie le formulaire HTTP comme le ferait l'utilisateur.
		response = self.client.post(
			# Sélectionne la route de demande à partir de son nom Django.
			reverse("auth_app:password_reset"),
			# Transmet l'adresse du compte de test au formulaire.
			{"email": self.user.email},
		)

		# La soumission doit rediriger vers la confirmation neutre.
		self.assertRedirects(response, reverse("auth_app:password_reset_done"))
		# Récupère la boîte mémoire remplie par le backend de test.
		from django.core import mail

		# Un seul courriel de réinitialisation doit être généré.
		self.assertEqual(len(mail.outbox), 1)
		# Le destinataire doit être exactement l'utilisateur ayant demandé le lien.
		self.assertEqual(mail.outbox[0].to, [self.user.email])
		# Le corps du courriel doit contenir l'URL de confirmation avec son jeton.
		self.assertIn("/api/auth/reset/", mail.outbox[0].body)

	# Vérifie que le lien d'oubli de mot de passe de la modale pointe vers le formulaire.
	def test_login_template_links_to_password_reset(self):
		# Ouvre la page qui contient la modale de connexion.
		response = self.client.get(reverse("auth_app:interface-login-page"))
		# Le lien doit afficher l'URL résolue de la demande de réinitialisation.
		self.assertContains(response, reverse("auth_app:password_reset"))

	def test_unknown_email_gets_same_confirmation_without_email(self):
		from django.core import mail

		response = self.client.post(
			reverse("auth_app:password_reset"),
			{"email": "unknown@example.com"},
		)

		self.assertRedirects(response, reverse("auth_app:password_reset_done"))
		self.assertEqual(len(mail.outbox), 0)

	def test_valid_reset_token_changes_password(self):
		uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
		token = default_token_generator.make_token(self.user)
		reset_url = reverse(
			"auth_app:password_reset_confirm",
			kwargs={"uidb64": uidb64, "token": token},
		)
		self.client.get(reset_url, follow=True)

		response = self.client.post(
			reverse(
				"auth_app:password_reset_confirm",
				kwargs={"uidb64": uidb64, "token": "set-password"},
			),
			{
				"new_password1": "New-Strong-Password-2026!",
				"new_password2": "New-Strong-Password-2026!",
			},
		)

		self.user.refresh_from_db()
		self.assertRedirects(response, reverse("auth_app:password_reset_complete"))
		self.assertTrue(self.user.check_password("New-Strong-Password-2026!"))
