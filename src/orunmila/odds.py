"""Cotes -> probabilités (Phase 2).

IDÉE DE BASE
------------
Une cote de 2,00 veut dire : "si tu gagnes, tu reçois 2 fois ta mise".
Le bookmaker estime donc la probabilité à 1 / 2,00 = 50 %.

LE PIÈGE : LA MARGE
-------------------
Si tu convertis les 3 cotes d'un match (domicile, nul, extérieur), la
somme des probabilités dépasse 100 %. Exemple :
    cotes 2,0 / 3,0 / 3,0  ->  50 % + 33,3 % + 33,3 % = 116,7 %
Le surplus (16,7 % ici) est la MARGE du bookmaker : c'est son bénéfice.
Pour obtenir des probabilités "honnêtes", on retire cette marge en
divisant chaque probabilité par la somme (méthode proportionnelle).

Convention de l'ordre partout dans le projet : H (domicile), D (nul), A (extérieur).
"""

import numpy as np


def _raw_probabilities(odds_h, odds_d, odds_a) -> np.ndarray:
    """1 / cote pour chaque issue. Résultat : tableau de forme (n_matchs, 3)."""
    odds = np.column_stack(
        [np.asarray(odds_h, dtype=float), np.asarray(odds_d, dtype=float), np.asarray(odds_a, dtype=float)]
    )
    return 1.0 / odds


def overround(odds_h, odds_d, odds_a) -> np.ndarray:
    """Marge du bookmaker pour chaque match (0,05 = 5 %)."""
    return _raw_probabilities(odds_h, odds_d, odds_a).sum(axis=1) - 1.0


def remove_margin(odds_h, odds_d, odds_a) -> np.ndarray:
    """Probabilités sans la marge. Chaque ligne somme exactement à 1.

    Colonnes : [victoire domicile, nul, victoire extérieur].
    """
    raw = _raw_probabilities(odds_h, odds_d, odds_a)
    return raw / raw.sum(axis=1, keepdims=True)
