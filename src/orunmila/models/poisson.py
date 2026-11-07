"""Modèle v1 : loi de Poisson (PHASE 3, pas encore écrit).

Ce fichier est volontairement vide pour l'instant : on n'écrit le modèle
qu'après avoir mesuré le niveau des bookmakers (Phase 2).

CE QU'ON Y METTRA
-----------------
Idée : le nombre de buts d'une équipe dans un match suit à peu près une
loi de Poisson. Il suffit d'en connaître la moyenne.
    buts attendus domicile  = attaque(domicile) x défense(extérieur) x avantage du terrain
    buts attendus extérieur = attaque(extérieur) x défense(domicile)
On calcule ensuite la probabilité de chaque score (0-0, 1-0, 1-1, ...) et on
additionne pour obtenir : victoire domicile / nul / victoire extérieur,
et plus/moins de 2,5 buts.

CONTRAINTE : pour prédire un match, n'utiliser QUE les matchs précédents
(voir backtest.py).
"""
