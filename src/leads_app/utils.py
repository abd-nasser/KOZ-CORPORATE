from datetime import timedelta
from decimal import Decimal
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


from decimal import Decimal

def calculer_prix_financable(mensualite, duree_mois, taux_annuel, apport):
    mensualite = Decimal(str(mensualite))
    duree_mois = int(duree_mois)
    taux_annuel = Decimal(str(taux_annuel))
    apport = Decimal(str(apport))

    taux_mensuel = taux_annuel / Decimal('1200')

    if taux_mensuel == 0:
        capital = mensualite * duree_mois
    else:
        # (1 + taux_mensuel) ** (-duree_mois) — éviter l'exposant négatif direct sur Decimal
        facteur = (1 + taux_mensuel) ** duree_mois
        capital = mensualite * (1 - (1 / facteur)) / taux_mensuel

    return capital + apport


MARGE_BASSE = Decimal('0.80')
MARGE_HAUTE = Decimal('1.50')

def verifier_coherence(mensualite, duree_mois, taux_annuel, apport, prix_reel):
    prix_financable = calculer_prix_financable(mensualite, duree_mois, taux_annuel, apport)
    prix_reel = Decimal(str(prix_reel))

    trop_bas = prix_financable < prix_reel * MARGE_BASSE
    trop_haut = prix_financable > prix_reel * MARGE_HAUTE
    return (trop_bas or trop_haut), prix_financable

# utils.py
def calculer_mensualite(montant, taux_annuel, duree_mois):
    duree_mois = int(duree_mois) if duree_mois else 0
    montant = Decimal(str(montant)) if montant else Decimal('0')

    if not montant or not duree_mois:
        return Decimal('0')

    if not taux_annuel or taux_annuel <= 0:
        return montant / duree_mois

    taux_mensuel = Decimal(str(taux_annuel)) / Decimal('1200')
    facteur = (1 + taux_mensuel) ** duree_mois  # exposant positif, sûr
    return montant * (taux_mensuel / (1 - (1 / facteur)))