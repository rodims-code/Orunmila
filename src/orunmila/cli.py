"""Interface terminal d'Orunmila.

C'est ici que sont définies les commandes que tu tapes dans le terminal :

    python -m orunmila --help       liste des commandes
    python -m orunmila info         état du projet
    python -m orunmila download     Phase 1 : télécharge et nettoie les données
    python -m orunmila baseline     Phase 2 : mesure le niveau des bookmakers

Chaque fonction décorée par @app.command() devient une commande.
Le nom de la fonction = le nom de la commande.
(La librairie "typer" fait ce travail à notre place.)
"""

from typing import List, Optional

import typer

from orunmila import __version__
from orunmila.data import (
    DEFAULT_SEASONS,
    PROCESSED_FILE,
    build_dataset,
    load_dataset,
    quality_report,
    save_dataset,
)
from orunmila.metrics import base_rate_reference, evaluate_odds_source

app = typer.Typer(
    help="Orunmila : un modèle statistique bat-il les bookmakers ? (terminal uniquement, pour l'instant)",
    no_args_is_help=True,
    add_completion=False,
)

SOURCE_LABELS = {"pin": "Pinnacle", "avg": "Moyenne du marché", "b365": "Bet365"}


@app.command()
def info() -> None:
    """Affiche la version et l'état du projet."""
    typer.echo(f"Orunmila v{__version__}")
    typer.echo("Phase en cours : Phase 2 (données + niveau des bookmakers)")
    if PROCESSED_FILE.exists():
        typer.echo(f"Données : OK ({PROCESSED_FILE})")
    else:
        typer.echo("Données : pas encore téléchargées -> lance  python -m orunmila download")


@app.command()
def download(
    season: Optional[List[str]] = typer.Option(
        None, "--season", "-s", help="Saison à charger, ex: 2324. Répétable. Par défaut : 2019-20 à 2025-26."
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Retélécharge même si le fichier existe déjà."),
) -> None:
    """Phase 1 : télécharge, nettoie et fusionne les saisons de la Premier League."""
    seasons = season or DEFAULT_SEASONS
    typer.echo(f"Saisons demandées : {', '.join(seasons)}")
    df = build_dataset(seasons, force=force)
    path = save_dataset(df)
    report = quality_report(df)

    typer.echo("")
    typer.echo("=== Rapport de qualité ===")
    typer.echo(f"Matchs       : {report['matches']}")
    typer.echo(f"Saisons      : {report['seasons']}")
    typer.echo(f"Équipes      : {report['teams']}")
    typer.echo(f"Période      : {report['date_min']} -> {report['date_max']}")
    typer.echo(f"Doublons     : {report['duplicates']}")
    typer.echo("Matchs par saison (une saison complète = 380) :")
    for s, count in report["matches_per_season"].items():
        flag = "" if count == 380 else "   <- incomplète ou anormale"
        typer.echo(f"  {s} : {count}{flag}")
    typer.echo("Part des matchs avec cotes :")
    for prefix, share in report["odds_coverage"].items():
        typer.echo(f"  {SOURCE_LABELS[prefix]:<20} {share:6.1%}")
    typer.echo("")
    typer.echo(f"Fichier sauvegardé : {path}")


@app.command()
def baseline() -> None:
    """Phase 2 : mesure la qualité des probabilités des bookmakers (le niveau à battre)."""
    df = load_dataset()
    typer.echo(f"Matchs analysés : {len(df)}")
    typer.echo("")
    typer.echo(f"{'Source':<26}{'Matchs':>8}{'Marge':>9}{'LogLoss':>10}{'Brier':>9}")
    typer.echo("-" * 62)

    typer.echo(f"{'Hasard (1/3 chacun)':<26}{len(df):>8}{'-':>9}{1.0986:>10.4f}{0.6667:>9.4f}")

    reference = base_rate_reference(df)
    typer.echo(
        f"{'Fréquences historiques':<26}{len(df):>8}{'-':>9}"
        f"{reference['log_loss']:>10.4f}{reference['brier']:>9.4f}"
    )

    for prefix, label in SOURCE_LABELS.items():
        result = evaluate_odds_source(df, prefix)
        if result is None:
            typer.echo(f"{label:<26}{'aucune cote dans les données':>40}")
            continue
        typer.echo(
            f"{label:<26}{result['matches']:>8}{result['margin']:>9.1%}"
            f"{result['log_loss']:>10.4f}{result['brier']:>9.4f}"
        )

    typer.echo("")
    typer.echo("Lecture : plus le LogLoss et le Brier sont BAS, meilleures sont les probabilités.")
    typer.echo("Ton futur modèle devra s'approcher de la ligne des bookmakers, pas du hasard.")
    typer.echo("Note le chiffre de référence dans EXPERIMENTS.md (Expérience 1).")
