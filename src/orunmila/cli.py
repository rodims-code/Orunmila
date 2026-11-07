"""Interface terminal d'Orunmila.

C'est ici que sont définies les commandes que tu tapes dans le terminal :

    python -m orunmila --help       liste des commandes
    python -m orunmila info         état du projet
    python -m orunmila download     Phase 1 : télécharge et nettoie les données
    python -m orunmila baseline     Phase 2 : mesure le niveau des bookmakers

Chaque fonction décorée par @app.command() devient une commande.
Le rendu visuel passe entièrement par `ui.py`.
"""

from typing import List, Optional

import typer

from orunmila import __version__, ui
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


@app.callback()
def main(
    plain: bool = typer.Option(
        False, "--plain", help="Désactive le formatage enrichi et les couleurs (pour logs bruts)."
    ),
) -> None:
    """Option globale pour contrôler le style d'affichage."""
    if plain:
        ui.set_plain(True)


@app.command()
def info(
    plain: bool = typer.Option(False, "--plain", help="Désactive le formatage enrichi."),
) -> None:
    """Affiche la version et l'état du projet."""
    if plain:
        ui.set_plain(True)
    ui.print_info(
        version=__version__,
        phase="Phase 3 (Modèle v1 Poisson)",
        data_path=PROCESSED_FILE,
        data_exists=PROCESSED_FILE.exists(),
    )


@app.command()
def download(
    season: Optional[List[str]] = typer.Option(
        None, "--season", "-s", help="Saison à charger, ex: 2324. Répétable. Par défaut : 2019-20 à 2025-26."
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Retélécharge même si le fichier existe déjà."),
    plain: bool = typer.Option(False, "--plain", help="Désactive le formatage enrichi."),
) -> None:
    """Phase 1 : télécharge, nettoie et fusionne les saisons de la Premier League."""
    if plain:
        ui.set_plain(True)
    seasons = season or DEFAULT_SEASONS
    ui.print_download_start(seasons)
    df = build_dataset(seasons, force=force)
    path = save_dataset(df)
    report = quality_report(df)
    ui.print_quality_report(report, path, SOURCE_LABELS)


@app.command()
def baseline(
    plain: bool = typer.Option(False, "--plain", help="Désactive le formatage enrichi."),
) -> None:
    """Phase 2 : mesure la qualité des probabilités des bookmakers (le niveau à battre)."""
    if plain:
        ui.set_plain(True)
    if not PROCESSED_FILE.exists():
        ui.print_error(
            f"Fichier de données introuvable : {PROCESSED_FILE}",
            suggest_command="python -m orunmila download",
        )
        raise typer.Exit(code=1)

    df = load_dataset()
    rows = []

    # Hasard (1/3 pour chaque issue)
    rows.append({
        "label": "Hasard (1/3 chacun)",
        "matches": len(df),
        "margin": "-",
        "log_loss": 1.0986,
        "brier": 0.6667,
    })

    # Fréquences historiques de la ligue
    reference = base_rate_reference(df)
    rows.append({
        "label": "Fréquences historiques",
        "matches": len(df),
        "margin": "-",
        "log_loss": reference["log_loss"],
        "brier": reference["brier"],
    })

    # Bookmakers
    for prefix, label in SOURCE_LABELS.items():
        result = evaluate_odds_source(df, prefix)
        if result is None:
            continue
        rows.append({
            "label": label,
            "matches": result["matches"],
            "margin": result["margin"],
            "log_loss": result["log_loss"],
            "brier": result["brier"],
        })

    ui.print_baseline_results(len(df), rows, SOURCE_LABELS)
