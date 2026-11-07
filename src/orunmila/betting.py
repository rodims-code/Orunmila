"""Simulation de paris (PHASE 4, pas encore écrit).

Ce fichier ne place JAMAIS de vrais paris. Il simule seulement, sur des
matchs passés, ce qui se serait passé.

RÈGLE PRÉVUE
------------
On "parie" (virtuellement) si :
    probabilité du modèle x cote  >  1,05
C'est-à-dire un avantage d'au moins 5 % sur la cote (seuil réglable).
Mise fixe : 1 unité. Pas de Kelly à ce stade (phase 7).

MESURES (via metrics.py) : ROI, nombre de paris, taux de réussite,
pire série de pertes (drawdown), courbe de bénéfice cumulé.
"""
