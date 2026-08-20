from datetime import timedelta
from django.utils import timezone


def generer_echeances_demande(demande):
    """Génère les échéances à partir d'une demande de financement"""
    echeances = []
    date_debut = timezone.now().date() + timedelta(days=30)

    for i in range(demande.duree_mois):
        echeance = {
            'numero': i + 1,
            'date': (date_debut + timedelta(days=30 * i)).isoformat(),
            'montant': float(demande.mensualite),
            'paye': False,
            'date_paiement': None,
        }
        echeances.append(echeance)
    return echeances


def generer_echeances_offre(offre):
    """Génère les échéances à partir d'une offre de financement"""
    echeances = []
    date_debut = timezone.now().date() + timedelta(days=30)

    for i in range(offre.duree_mois):
        echeance = {
            'numero': i + 1,
            'date': (date_debut + timedelta(days=30 * i)).isoformat(),
            'montant': float(offre.mensualite),
            'paye': False,
            'date_paiement': None,
        }
        echeances.append(echeance)
    return echeances