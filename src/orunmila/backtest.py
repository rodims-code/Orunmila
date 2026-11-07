"""Backtest "walk-forward" (PHASE 3, pas encore écrit).

PRINCIPE
--------
Un backtest rejoue le passé : "si j'avais utilisé mon modèle à
l'époque, qu'aurait-il prédit ?"

RÈGLE D'OR : pour prédire un match du 15 mars, le modèle n'a le droit
de connaître QUE les matchs joués avant le 15 mars. Sinon il "triche"
sans le vouloir (fuite de données) et les résultats sont faux.

Étapes prévues :
    pour chaque match, dans l'ordre chronologique :
        1. entraîner le modèle sur les matchs passés uniquement
        2. prédire les probabilités de ce match
        3. les stocker
    puis comparer le log loss du modèle à celui des bookmakers.
"""
