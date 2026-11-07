from types import SimpleNamespace

from django.test import SimpleTestCase

from .forms import DocumentsUploadForm


class DocumentsUploadFormRequiredFieldsTests(SimpleTestCase):
	def test_fiche_demande_is_required_for_entrepreneurs(self):
		form = DocumentsUploadForm(
			client=SimpleNamespace(profession_choisie='entrepreneur')
		)

		self.assertTrue(form.fields['fiche_demande'].required)

	def test_fiche_demande_is_optional_for_non_entrepreneurs(self):
		form = DocumentsUploadForm(
			client=SimpleNamespace(profession_choisie='salarie')
		)

		self.assertFalse(form.fields['fiche_demande'].required)

	def test_reglement_interieur_is_optional_for_entrepreneurs(self):
		form = DocumentsUploadForm(
			client=SimpleNamespace(profession_choisie='entrepreneur')
		)

		self.assertFalse(form.fields['reglement_interieur'].required)
