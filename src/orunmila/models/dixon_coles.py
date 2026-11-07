"""Correction Dixon-Coles (PHASE 6, amélioration n°2, pas encore écrit).

Poisson gère mal les petits scores (0-0, 1-0, 0-1, 1-1) : ils arrivent
plus ou moins souvent que prévu. Dixon-Coles ajoute un petit coefficient
de correction sur ces scores.

On ne l'écrit qu'après le verdict de la phase 5, et on le garde
uniquement si le log loss baisse (un changement à la fois).
"""
