"""Les "règles de notation" du projet.

Pour savoir si un modèle est bon, il faut un chiffre. Ce fichier contient
les chiffres qu'on utilise.

- log_loss : note la qualité des probabilités. PLUS BAS = MIEUX.
    Si tu donnes 70 % à un événement qui arrive, tu es peu pénalisé.
    Si tu donnes 5 % à un événement qui arrive, tu es très pénalisé.
    Repères pour un match (3 issues) :
        1,0986  = tirage au hasard (1/3 chacun), le pire "raisonnable"
        ~0,98   = ordre de grandeur des meilleurs bookmakers (à vérifier)
- brier_score : autre note de qualité des probabilités. PLUS BAS = MIEUX.
- roi : bénéfice divisé par le total misé (0,03 = +3 %).
- max_drawdown : la plus grosse chute depuis un sommet du bénéfice cumulé
    (le pire moment que tu aurais vécu).

Ordre des colonnes de probabilités : H (domicile), D (nul), A (extérieur).
"""

import numpy as np
import pandas as pd

from orunmila.odds import overround, remove_margin

EPS = 1e-15  # évite log(0), qui donnerait l'infini
_RESULT_TO_INDEX = {"H": 0, "D": 1, "A": 2}


def result_to_index(results) -> np.ndarray:
    """Transforme ["H", "D", "A"] en [0, 1, 2]."""
    return np.array([_RESULT_TO_INDEX[r] for r in results], dtype=int)


def log_loss(probs, outcomes) -> float:
    """Log loss moyen. probs : (n, 3). outcomes : indices 0/1/2 de l'issue réelle."""
    probs = np.clip(np.asarray(probs, dtype=float), EPS, 1.0)
    outcomes = np.asarray(outcomes, dtype=int)
    probability_given_to_truth = probs[np.arange(len(outcomes)), outcomes]
    return float(-np.mean(np.log(probability_given_to_truth)))


def brier_score(probs, outcomes) -> float:
    """Score de Brier moyen (version 3 issues)."""
    probs = np.asarray(probs, dtype=float)
    outcomes = np.asarray(outcomes, dtype=int)
    truth = np.zeros_like(probs)
    truth[np.arange(len(outcomes)), outcomes] = 1.0
    return float(np.mean(np.sum((probs - truth) ** 2, axis=1)))


def roi(profits, stakes) -> float:
    """Bénéfice total / total misé. Renvoie nan s'il n'y a aucune mise."""
    total_staked = float(np.sum(stakes))
    if total_staked == 0:
        return float("nan")
    return float(np.sum(profits)) / total_staked


def max_drawdown(profits) -> float:
    """Plus grosse chute du bénéfice cumulé depuis son dernier sommet."""
    cumulative = np.concatenate([[0.0], np.cumsum(np.asarray(profits, dtype=float))])
    peak = np.maximum.accumulate(cumulative)
    return float(np.max(peak - cumulative))


# ----------------------------------------------------------------------
# Phase 2 : le niveau à battre
# ----------------------------------------------------------------------
def evaluate_odds_source(df: pd.DataFrame, prefix: str) -> dict | None:
    """Mesure la qualité des probabilités d'un bookmaker (sa marge retirée).

    prefix : "pin" (Pinnacle), "avg" (moyenne du marché) ou "b365" (Bet365).
    Renvoie None si ce bookmaker n'a aucune cote dans les données.
    """
    columns = [f"{prefix}_h", f"{prefix}_d", f"{prefix}_a"]
    sub = df.dropna(subset=columns)
    if sub.empty:
        return None
    odds_h, odds_d, odds_a = (sub[c] for c in columns)
    probs = remove_margin(odds_h, odds_d, odds_a)
    outcomes = result_to_index(sub["result"])
    return {
        "matches": len(sub),
        "margin": float(np.mean(overround(odds_h, odds_d, odds_a))),
        "log_loss": log_loss(probs, outcomes),
        "brier": brier_score(probs, outcomes),
    }


def base_rate_reference(df: pd.DataFrame) -> dict:
    """Modèle "bête" : donne toujours les fréquences historiques (ex. 45 % / 25 % / 30 %).

    Sert de plancher : un vrai modèle doit faire mieux que ça.
    (Les fréquences sont calculées sur tout le jeu de données : c'est
    acceptable pour 3 chiffres seulement, et ce n'est qu'un repère.)
    """
    outcomes = result_to_index(df["result"])
    freq = np.bincount(outcomes, minlength=3) / len(outcomes)
    probs = np.tile(freq, (len(outcomes), 1))
    return {
        "frequencies": freq,
        "log_loss": log_loss(probs, outcomes),
        "brier": brier_score(probs, outcomes),
    }
