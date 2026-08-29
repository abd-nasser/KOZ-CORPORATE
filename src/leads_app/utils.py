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


def calculer_prix_financable(mensualite, duree_mois, taux_annuel, apport):
    taux_mensuel = (taux_annuel / 100.0) / 12.0
    if taux_mensuel == 0:
        capital = mensualite * duree_mois
    else:
        capital = mensualite * (1 - (1 + taux_mensuel) ** (-duree_mois)) / taux_mensuel
    return capital + apport


MARGE_BASSE = Decimal('0.80')   # ← ✅ DECIMAL
MARGE_HAUTE = Decimal('1.50')   # ← ✅ DECIMAL # ni dépasser 150% du prix réel (mensualité trop grosse pour la durée)

def verifier_coherence(mensualite, duree_mois, taux_annuel, apport, prix_reel):
    prix_financable = calculer_prix_financable(mensualite, duree_mois, taux_annuel, apport)
    trop_bas = prix_financable < prix_reel * MARGE_BASSE
    trop_haut = prix_financable > prix_reel * MARGE_HAUTE
    return trop_bas or trop_haut, prix_financable


# utils.py
def calculer_mensualite(montant, taux_annuel, duree_mois):
    from decimal import Decimal
    if not montant or not duree_mois:
        return Decimal('0')
    if not taux_annuel or taux_annuel <= 0:
        return Decimal(str(montant)) / Decimal(str(duree_mois))
    
    taux_mensuel = Decimal(str(taux_annuel)) / Decimal('1200')
    facteur = (1 + taux_mensuel) ** (-Decimal(str(duree_mois)))
    return montant * (taux_mensuel / (1 - facteur))