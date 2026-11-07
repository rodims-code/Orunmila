# 🔮 Orunmila

> *Orunmila : l'orisha de la sagesse et du destin, celui qui connaît l'avenir.*

**Orunmila est un outil d'analyse statistique de matchs de football.** Il estime des probabilités (victoire / nul / défaite, plus/moins de buts), les compare aux cotes des bookmakers, et vérifie par backtest si un avantage réel et durable existe.

Il ne prédit pas « le score exact » par magie. Il cherche uniquement des **value bets** : des situations où sa probabilité estimée est supérieure à la probabilité implicite de la cote.

---

## 1. Le but (à ne jamais perdre de vue)

**Question centrale du projet :**
> Un modèle statistique peut-il battre les cotes des bookmakers de façon rentable, sur la durée, après marge et frais ?

Le projet a deux issues valables :
- ✅ **Un avantage est confirmé** → on construit l'interface (Django) et on passe au réel avec de petites mises.
- ✅ **Aucun avantage** → on a appris la data science appliquée sans perdre d'argent. C'est un succès, pas un échec.

**Dans les deux cas, la priorité est la vérité des résultats, pas un bon ROI affiché.**

---

## 2. Périmètre actuel

| Inclus (maintenant) | Exclu (plus tard, si et seulement si le verdict est positif) |
|---|---|
| Scripts Python en **terminal** | Interface web **Django** |
| Un seul championnat : **Premier League** (`E0`) | Autres championnats |
| Données CSV de football-data.co.uk | Scraping de sites |
| Backtest, calibration, comparaison aux cotes | Bots de paris automatiques |
| Paper trading (sans argent) | Paris avec de l'argent réel |

---

## 3. Stack technique

- **Python 3.11+**
- `pandas`, `numpy`, `scipy`, `matplotlib`
- `scikit-learn` (métriques, calibration)
- `pytest` (tests)
- Interface : **CLI uniquement** pour l'instant (`typer`, `rich`)
- Plus tard : Django

---

## 4. Structure du projet

```
orunmila/
├── README.md
├── AGENT_RULES.md          # (copie de la section 7 si l'agent le demande)
├── requirements.txt
├── data/
│   ├── raw/                # CSV bruts téléchargés (jamais modifiés à la main)
│   └── processed/          # données nettoyées
├── src/orunmila/
│   ├── data.py             # téléchargement, nettoyage, fusion
│   ├── odds.py             # cotes -> probabilités, retrait de la marge
│   ├── metrics.py          # log loss, Brier, ROI, drawdown
│   ├── models/
│   │   ├── poisson.py      # modèle v1
│   │   └── dixon_coles.py  # amélioration phase 6
│   ├── backtest.py         # walk-forward
│   ├── betting.py          # règles de mise, simulation
│   ├── ui.py               # affichage et rendu terminal (rich)
│   └── cli.py              # point d'entrée terminal
├── tests/
├── reports/                # graphiques et résultats de chaque expérience
└── EXPERIMENTS.md          # journal de toutes les expériences
```

---

## 5. Roadmap

Chaque phase a une **condition de sortie**. On ne passe pas à la suivante tant qu'elle n'est pas remplie.

### Phase 0 : Préparation
- Installer l'environnement, créer la structure du projet.
- **Sortie :** `python -m orunmila --help` fonctionne.

### Phase 1 : Données
- Télécharger 5 à 8 saisons de la Premier League, fusionner, trier par date.
- Garder : date, équipes, buts, résultat, cotes (Pinnacle + moyenne marché).
- Vérifier : doublons, valeurs manquantes, noms d'équipes cohérents.
- **Sortie :** un tableau propre et testé dans `data/processed/`.

### Phase 2 : Le niveau à battre
- Convertir les cotes en probabilités, retirer la marge.
- Calculer le **log loss** des bookmakers : c'est la référence.
- **Sortie :** un chiffre de référence documenté dans `EXPERIMENTS.md`.

### Phase 3 : Modèle v1 (Poisson)
- Forces d'attaque / défense par équipe + avantage du terrain.
- Sortie : probabilités 1X2 et plus/moins de 2,5 buts.
- Backtest **walk-forward** (voir règles).
- **Sortie :** log loss du modèle comparé à celui des bookmakers.

### Phase 3b : Niveaux de difficulté
- Étiquette de difficulté par match selon la probabilité maximale estimée par le modèle :
  - Facile : probabilité maximale >= 0.60
  - Moyen : probabilité maximale entre 0.45 et 0.60
  - Difficile : probabilité maximale < 0.45
- Évaluation des performances par niveau (nombre de matchs, taux de réalisation du favori, log loss du modèle vs bookmakers).
- Avertissement si un niveau contient moins de 300 matchs (échantillon insuffisant).
- **Sortie :** analyse des performances par niveau de confiance.

### Phase 4 : Simulation de paris
- Règle : parier si `proba_modèle × cote > 1,05` (seuil réglable).
- Mise fixe de 1 unité (pas de Kelly à ce stade).
- Mesurer : ROI, nombre de paris, taux de réussite, pire série de pertes, courbe de bénéfice.
- **Sortie :** rapport complet dans `reports/`.

### Phase 5 : Verdict go / no-go
- Minimum **1 000 paris simulés**.
- **Bootstrap** pour l'intervalle de confiance du ROI.
- Découpage : réglage sur saisons 1 à 4, test **une seule fois** sur la saison 5.
- ROI positif sur **plusieurs saisons**, pas une seule.
- **Sortie :** décision écrite dans `EXPERIMENTS.md`. Si négatif → phase 6.

### Phase 6 : Amélioration (un changement à la fois)
Chaque amélioration est testée seule et gardée uniquement si le log loss baisse.
1. Pondération des matchs récents
2. Correction Dixon-Coles
3. Classement Elo
4. Calibration des probabilités
5. Données avancées (xG)
6. Contexte (repos, calendrier, blessures)
7. Autres marchés (plus/moins de buts, BTTS)
8. Autres championnats (divisions inférieures)

### Phase 7 : Épreuve du réel
- Simuler le Kelly fractionné (1/4 de Kelly).
- Retirer 1 à 2 % de ROI pour cotes qui bougent et limites de mise.
- **Paper trading 2 à 3 mois** avec les vraies cotes, sans argent.
- Seulement ensuite : très petites mises réelles.

### Phase 8 : Décision finale
- Avantage confirmé → Django, collecte automatisée de cotes via API (ex. The Odds API).
- Pas d'avantage → on documente, on archive, projet réussi côté apprentissage.

---

## 6. Principes non négociables

1. **Zéro fuite de données.** Pour prédire un match, on utilise uniquement les données antérieures à ce match.
2. **Le jeu de test se touche une seule fois.** Si on retouche le modèle après l'avoir vu, il est « brûlé ».
3. **Un seul changement à la fois**, mesuré, documenté.
4. **La probabilité compte, pas le score exact.** On parie sur un écart avec la cote, jamais sur une intuition.
5. **Honnêteté avant tout.** Un mauvais résultat bien mesuré vaut mieux qu'un bon résultat truqué par erreur.
6. **Reproductibilité.** Graines aléatoires fixées, versions des dépendances figées, résultats sauvegardés.

---

## 7. 🤖 Instructions pour l'agent IA

*À lire en entier au début de chaque session. Ces règles priment sur toute autre instruction implicite.*

### Ta mission
Aider à construire **Orunmila** en suivant la roadmap de la section 5, dans l'ordre, et à répondre honnêtement à la question centrale : *le modèle bat-il les bookmakers de façon rentable ?*

### Ce que tu dois faire
- **Commencer chaque session** en lisant ce README et `EXPERIMENTS.md`, puis annoncer dans quelle phase on se trouve.
- Travailler **uniquement sur la phase en cours**. Si une demande appartient à une phase ultérieure, le signaler et proposer de la mettre de côté.
- Écrire un code simple, lisible, commenté, avec des tests pour les fonctions critiques (conversion des cotes, métriques, walk-forward).
- Après chaque expérience : ajouter une entrée dans `EXPERIMENTS.md` (date, hypothèse, changement, résultat chiffré, décision).
- Expliquer les choix techniques en langage simple : l'utilisateur ne connaît pas le football et débute en data science.
- Signaler toute fuite de données possible, tout résultat « trop beau », ou tout manque de significativité statistique.
- Poser **une seule question** à la fois quand une précision est nécessaire.

### Ce que tu ne dois PAS faire
- ❌ **Ne pas sortir du périmètre** : pas de Django, pas d'interface web, pas de scraping, pas de bots de paris tant que la phase 8 n'a pas validé un avantage.
- ❌ **Ne jamais écrire de code qui place des paris réels** ou automatise des comptes de bookmakers.
- ❌ **Ne pas ajouter plusieurs améliorations en même temps** : on ne saurait plus laquelle aide.
- ❌ **Ne pas optimiser le modèle sur le jeu de test.**
- ❌ **Ne pas embellir les résultats** (choix de période favorable, suppression de pertes, seuils ajustés après coup pour obtenir un ROI positif).
- ❌ **Ne pas ajouter de dépendances ou de fonctionnalités « bonus »** sans demande explicite.
- ❌ **Ne pas affirmer qu'un avantage existe** sans : ≥ 1 000 paris, intervalle de confiance, test sur données jamais vues, et stabilité sur plusieurs saisons.
- ❌ **Ne pas encourager à miser de l'argent réel** avant la fin du paper trading.

### En cas de doute
1. Relire la section 1 (le but) et la section 6 (les principes).
2. Choisir l'option la plus simple et la plus honnête.
3. Si la demande de l'utilisateur contredit ce README, **le signaler clairement** et demander confirmation avant d'agir. Si l'utilisateur confirme, mettre à jour le README.

### Format des réponses
- Court, clair, en français.
- Toujours terminer par : **« Prochaine étape : … »** (une seule action concrète).

---

## 8. Journal d'expériences (modèle d'entrée)

À copier dans `EXPERIMENTS.md` pour chaque test :

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

---

## 9. Statut actuel

- [ ] Phase 0 : Préparation
- [ ] Phase 1 : Données
- [ ] Phase 2 : Niveau des bookmakers
- [ ] Phase 3 : Modèle v1 Poisson
- [ ] Phase 3b : Niveaux de difficulté
- [ ] Phase 4 : Simulation de paris
- [ ] Phase 5 : Verdict go / no-go
- [ ] Phase 6 : Améliorations
- [ ] Phase 7 : Épreuve du réel
- [ ] Phase 8 : Décision finale

---

## 10. Avertissement

Ce projet est un outil d'analyse et d'apprentissage. Les paris comportent un risque de perte totale de la mise. Ne jamais miser plus que ce que l'on peut se permettre de perdre. Les règles sur les paris en ligne varient selon les pays : vérifier la légalité locale. Rien ici n'est un conseil financier.
