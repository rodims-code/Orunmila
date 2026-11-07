# Journal d'expériences d'Orunmila

Chaque test est noté ici, avec son résultat chiffré et la décision prise.
Un résultat mauvais mais bien mesuré est précieux : ne jamais l'effacer.

Pour chaque expérience, copier le modèle d'entrée en bas de ce fichier.

---

## Expérience 1 : niveau de référence des bookmakers (Phase 2)

- Date :
- Phase : 2
- Hypothèse : les probabilités des bookmakers (marge retirée) sont notre référence. Un modèle qui ne s'en approche pas ne vaut pas la peine d'être testé en paris.
- Changement effectué : aucun, c'est une mesure.
- Données utilisées : Premier League, saisons 2019-20 à 2025-26 (`python -m orunmila download`)
- Commande : `python -m orunmila baseline`
- Résultats (à remplir après la commande) :
  - Hasard (1/3 chacun) : log loss = 1.0986
  - Fréquences historiques : log loss = …
  - Pinnacle : log loss = … | marge = …
  - Moyenne du marché : log loss = … | marge = …
  - Bet365 : log loss = … | marge = …
- Comparaison avec la référence bookmakers : sans objet (c'est la référence)
- Décision : le chiffre à battre est le log loss de … (à choisir : la source la plus précise, souvent Pinnacle)

---

## Modèle d'entrée (à copier pour chaque nouvelle expérience)

```
### Expérience N : <titre>
- Date :
- Phase :
- Hypothèse :
- Changement effectué (un seul) :
- Données utilisées (saisons, train / test) :
- Résultats : log loss = … | ROI = … | nb paris = … | pire série = …
- Comparaison avec la référence bookmakers :
- Décision : gardé / rejeté, et pourquoi
```
