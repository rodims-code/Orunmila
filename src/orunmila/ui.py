"""Module d'interface et de rendu terminal pour Orunmila.

Inspiré du style sobre et élégant de Claude Code :
- Titre sobre avec nom, version et phase active
- Couleur d'accentuation corail/orange (orange3) et tons neutres/gris
- Vert (✓) pour les succès, rouge (✗) pour les erreurs, orange (●) pour l'en-cours
- Tableaux nets et panneaux arrondis (box.ROUNDED)
- Support du mode brut via --plain pour des logs sans style
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text

# Console Rich par défaut (gère l'encodage UTF-8 sous Windows)
console = Console()

# Drapeau global pour désactiver tout formatage enrichi (--plain)
_plain_mode: bool = False


def set_plain(plain: bool) -> None:
    """Active ou désactive le mode texte brut."""
    global _plain_mode
    _plain_mode = plain


def is_plain() -> bool:
    """Indique si le mode texte brut est actif."""
    return _plain_mode


def print_header(version: str, phase: str = "Phase 3 (Modèle v1 Poisson)") -> None:
    """Affiche le bandeau d'en-tête sobre du projet."""
    if is_plain():
        print(f"Orunmila v{version} | {phase}")
        print("=" * 60)
        return

    title_text = Text()
    title_text.append("◆ ORUNMILA ", style="bold orange3")
    title_text.append(f"v{version}", style="dim")
    title_text.append("  |  ", style="dim")
    title_text.append(phase, style="italic")

    panel = Panel(
        title_text,
        box=box.ROUNDED,
        border_style="orange3",
        padding=(0, 1),
    )
    console.print(panel)


def print_info(version: str, phase: str, data_path: Path, data_exists: bool) -> None:
    """Rendu de la commande `info`."""
    if is_plain():
        print(f"Orunmila v{version}")
        print(f"Phase en cours : {phase}")
        if data_exists:
            print(f"Données : OK ({data_path})")
        else:
            print(f"Données : pas encore téléchargées -> lance  python -m orunmila download")
        return

    print_header(version, phase)
    console.print()

    table = Table(box=box.ROUNDED, show_header=False, border_style="grey37")
    table.add_column("Propriété", style="bold")
    table.add_column("Valeur")

    table.add_row("Version", f"[orange3]{version}[/orange3]")
    table.add_row("Phase", phase)

    if data_exists:
        table.add_row("Données", f"[green]✓ OK[/green] [dim]({data_path})[/dim]")
    else:
        table.add_row(
            "Données",
            "[red]✗ Manquantes[/red] [dim]-> lance[/dim] [bold orange3]python -m orunmila download[/bold orange3]",
        )

    console.print(table)


def print_download_start(seasons: List[str]) -> None:
    """Affiche le début du téléchargement."""
    if is_plain():
        print(f"Saisons demandées : {', '.join(seasons)}")
    else:
        console.print(f"[dim]● Saisons demandées :[/dim] [orange3]{', '.join(seasons)}[/orange3]")


def create_progress_bar() -> Progress:
    """Crée une barre de progression adaptée au terminal."""
    if is_plain():
        return Progress(TextColumn("{task.description}"), console=Console(quiet=True))

    return Progress(
        SpinnerColumn(spinner_name="dots", style="orange3"),
        TextColumn("[bold]{task.description}[/bold]"),
        BarColumn(bar_width=30, style="grey37", complete_style="orange3"),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console,
    )


def print_quality_report(report: Dict[str, Any], file_path: Path, source_labels: Dict[str, str]) -> None:
    """Affiche le rapport de qualité du jeu de données téléchargé."""
    if is_plain():
        print("")
        print("=== Rapport de qualité ===")
        print(f"Matchs       : {report['matches']}")
        print(f"Saisons      : {report['seasons']}")
        print(f"Équipes      : {report['teams']}")
        print(f"Période      : {report['date_min']} -> {report['date_max']}")
        print(f"Doublons     : {report['duplicates']}")
        print("Matchs par saison (une saison complète = 380) :")
        for s, count in report["matches_per_season"].items():
            flag = "" if count == 380 else "   <- incomplète ou anormale"
            print(f"  {s} : {count}{flag}")
        print("Part des matchs avec cotes :")
        for prefix, share in report["odds_coverage"].items():
            print(f"  {source_labels.get(prefix, prefix):<20} {share:6.1%}")
        print("")
        print(f"Fichier sauvegardé : {file_path}")
        return

    console.print()
    # Résumé général
    summary_table = Table(title="Rapport de qualité des données", box=box.ROUNDED, border_style="orange3")
    summary_table.add_column("Indicateur", style="bold")
    summary_table.add_column("Valeur", justify="right")

    summary_table.add_row("Total matchs", str(report["matches"]))
    summary_table.add_row("Nombre de saisons", str(report["seasons"]))
    summary_table.add_row("Équipes distinctes", str(report["teams"]))
    summary_table.add_row("Période", f"{report['date_min']} → {report['date_max']}")
    dup_style = "green" if report["duplicates"] == 0 else "red bold"
    summary_table.add_row("Doublons", f"[{dup_style}]{report['duplicates']}[/{dup_style}]")
    console.print(summary_table)

    # Répartition par saison
    seasons_table = Table(title="Matchs par saison (380 attendus)", box=box.ROUNDED, border_style="grey37")
    seasons_table.add_column("Saison", style="bold")
    seasons_table.add_column("Matchs", justify="right")
    seasons_table.add_column("Statut")

    for s, count in report["matches_per_season"].items():
        if count == 380:
            status = "[green]✓ Complète[/green]"
        else:
            status = f"[orange3]● Incomplète ({count}/380)[/orange3]"
        seasons_table.add_row(s, str(count), status)
    console.print(seasons_table)

    # Couverture des cotes
    odds_table = Table(title="Couverture des cotes bookmakers", box=box.ROUNDED, border_style="grey37")
    odds_table.add_column("Source", style="bold")
    odds_table.add_column("Couverture", justify="right")

    for prefix, share in report["odds_coverage"].items():
        label = source_labels.get(prefix, prefix)
        cov_color = "green" if share > 0.95 else ("yellow" if share > 0.50 else "red")
        odds_table.add_row(label, f"[{cov_color}]{share:6.1%}[/{cov_color}]")
    console.print(odds_table)

    console.print(f"[green]✓ Fichier sauvegardé :[/green] [dim]{file_path}[/dim]")


def print_baseline_results(
    total_matches: int,
    rows: List[Dict[str, Any]],
    source_labels: Dict[str, str],
) -> None:
    """Affiche les métriques de la ligne de base (Hasard, Historique, Bookmakers)."""
    if is_plain():
        print(f"Matchs analysés : {total_matches}")
        print("")
        print(f"{'Source':<26}{'Matchs':>8}{'Marge':>9}{'LogLoss':>10}{'Brier':>9}")
        print("-" * 62)
        for r in rows:
            margin_str = f"{r['margin']:>9.1%}" if isinstance(r["margin"], float) else f"{r['margin']:>9}"
            print(f"{r['label']:<26}{r['matches']:>8}{margin_str}{r['log_loss']:>10.4f}{r['brier']:>9.4f}")
        print("")
        print("Lecture : plus le LogLoss et le Brier sont BAS, meilleures sont les probabilités.")
        print("Ton futur modèle devra s'approcher de la ligne des bookmakers, pas du hasard.")
        print("Note le chiffre de référence dans EXPERIMENTS.md (Expérience 1).")
        return

    console.print(f"[dim]Matchs analysés :[/dim] [bold]{total_matches}[/bold]")
    console.print()

    table = Table(
        title="Mesure du niveau de référence (Phase 2)",
        box=box.ROUNDED,
        border_style="orange3",
        header_style="bold orange3",
    )
    table.add_column("Source", style="bold")
    table.add_column("Matchs", justify="right")
    table.add_column("Marge", justify="right")
    table.add_column("LogLoss", justify="right")
    table.add_column("Brier", justify="right")

    for r in rows:
        margin_str = f"{r['margin']:6.1%}" if isinstance(r["margin"], float) else str(r["margin"])
        # Mise en valeur subtile
        is_bm = r["label"] in source_labels.values()
        lbl_style = "bold orange3" if r["label"] == "Pinnacle" else ("white" if is_bm else "dim")
        table.add_row(
            Text(r["label"], style=lbl_style),
            str(r["matches"]),
            margin_str,
            f"{r['log_loss']:.4f}",
            f"{r['brier']:.4f}",
        )

    console.print(table)
    console.print(
        Panel(
            "[dim]• Plus le [bold]LogLoss[/bold] et le [bold]Brier[/bold] sont BAS, plus les probabilités sont exactes.\n"
            "• Le modèle Poisson (Phase 3) devra chercher à se rapprocher de la ligne des bookmakers (Pinnacle ~ 0.9623).\n"
            "• Chiffre à retenir pour EXPERIMENTS.md : [bold orange3]Pinnacle = 0.9623[/bold orange3].[/dim]",
            title="[bold]Repères statistiques[/bold]",
            box=box.ROUNDED,
            border_style="grey37",
        )
    )


def print_backtest_header(version: str, train_matches: int, eval_matches: int) -> None:
    """Affiche le bandeau pour le backtest."""
    if is_plain():
        print(f"Orunmila v{version} | Backtest Poisson walk-forward")
        print(f"Matchs de rodage (train initial) : {train_matches}")
        print(f"Matchs évalués (test)           : {eval_matches}")
        print("=" * 60)
        return

    print_header(version, "Phase 3 (Backtest Poisson walk-forward)")
    console.print(
        f"[dim]● Matchs d'apprentissage (rodage) :[/dim] [bold]{train_matches}[/bold]  |  "
        f"[dim]Matchs évalués :[/dim] [bold]{eval_matches}[/bold]"
    )
    console.print()


def print_backtest_results(
    eval_matches: int,
    metrics: Dict[str, Any],
    by_difficulty: Optional[Dict[str, Dict[str, Any]]] = None,
) -> None:
    """Affiche les résultats d'un backtest (global et optionnellement par difficulté)."""
    if is_plain():
        print("=== Résultats du Backtest (sur les MÊMES matchs) ===")
        print(f"Matchs évalués : {eval_matches}")
        print(f"{'Modèle':<24}{'LogLoss':>10}{'Brier':>10}")
        print("-" * 46)
        print(f"{'Poisson (notre modèle)':<24}{metrics['model_log_loss']:>10.4f}{metrics['model_brier']:>10.4f}")
        print(f"{'Pinnacle (référence)':<24}{metrics['pin_log_loss']:>10.4f}{metrics['pin_brier']:>10.4f}")
        print(f"{'Moyenne marché':<24}{metrics['avg_log_loss']:>10.4f}{metrics['avg_brier']:>10.4f}")

        if by_difficulty:
            print("")
            print("=== Découpage par niveau de difficulté (Phase 3b) ===")
            print(f"{'Niveau':<12}{'Matchs':>8}{'% Favori':>10}{'LL Modèle':>12}{'LL Bookmakers':>14}")
            print("-" * 58)
            for diff, data in by_difficulty.items():
                print(
                    f"{diff:<12}{data['count']:>8}{data['fav_rate']:>9.1%}"
                    f"{data['model_log_loss']:>12.4f}{data['pin_log_loss']:>14.4f}"
                )
                if data["count"] < 300:
                    print(f"  [ATTENTION] Échantillon trop petit ({data['count']} < 300) pour conclure.")
        return

    console.print()
    table = Table(
        title=f"Comparaison du Modèle vs Bookmakers ({eval_matches} matchs strictement identiques)",
        box=box.ROUNDED,
        border_style="orange3",
        header_style="bold orange3",
    )
    table.add_column("Prédiction", style="bold")
    table.add_column("LogLoss (↓)", justify="right")
    table.add_column("Score Brier (↓)", justify="right")
    table.add_column("Écart vs Pinnacle", justify="right")

    diff_ll = metrics["model_log_loss"] - metrics["pin_log_loss"]
    diff_brier = metrics["model_brier"] - metrics["pin_brier"]
    diff_str = f"+{diff_ll:.4f}" if diff_ll > 0 else f"{diff_ll:.4f}"

    table.add_row(
        Text("Poisson v1 (Orunmila)", style="bold orange3"),
        f"{metrics['model_log_loss']:.4f}",
        f"{metrics['model_brier']:.4f}",
        f"[red]{diff_str}[/red]" if diff_ll > 0 else f"[green]{diff_str}[/green]",
    )
    table.add_row(
        Text("Pinnacle (Bookmaker expert)", style="bold"),
        f"{metrics['pin_log_loss']:.4f}",
        f"{metrics['pin_brier']:.4f}",
        "[dim]référence (0)[/dim]",
    )
    table.add_row(
        Text("Moyenne du marché", style="dim"),
        f"{metrics['avg_log_loss']:.4f}",
        f"{metrics['avg_brier']:.4f}",
        f"+{metrics['avg_log_loss'] - metrics['pin_log_loss']:.4f}",
    )
    console.print(table)

    if by_difficulty:
        console.print()
        diff_table = Table(
            title="Performances par niveau de difficulté (Phase 3b)",
            box=box.ROUNDED,
            border_style="orange3",
            header_style="bold orange3",
        )
        diff_table.add_column("Niveau", style="bold")
        diff_table.add_column("Seuil max", style="dim")
        diff_table.add_column("Matchs", justify="right")
        diff_table.add_column("% Réussite favori", justify="right")
        diff_table.add_column("LogLoss Modèle", justify="right")
        diff_table.add_column("LogLoss Pinnacle", justify="right")
        diff_table.add_column("Fiabilité statistique", justify="center")

        level_rules = {
            "facile": "≥ 60%",
            "moyen": "45% à 60%",
            "difficile": "< 45%",
        }

        for diff, data in by_difficulty.items():
            valid = data["count"] >= 300
            valid_txt = "[green]✓ Suffisant[/green]" if valid else f"[red]✗ Faible (<300)[/red]"
            diff_table.add_row(
                diff.capitalize(),
                level_rules.get(diff.lower(), "-"),
                str(data["count"]),
                f"{data['fav_rate']:6.1%}",
                f"{data['model_log_loss']:.4f}",
                f"{data['pin_log_loss']:.4f}",
                valid_txt,
            )
        console.print(diff_table)


def print_error(message: str, suggest_command: Optional[str] = None) -> None:
    """Affiche un message d'erreur avec indication de correction."""
    if is_plain():
        print(f"ERREUR : {message}")
        if suggest_command:
            print(f"Pour corriger, exécute : {suggest_command}")
        return

    content = f"[red bold]✗ ERREUR :[/red bold] {message}"
    if suggest_command:
        content += f"\n\n[dim]Pour corriger, tape :[/dim]\n  [bold orange3]{suggest_command}[/bold orange3]"
    console.print(Panel(content, box=box.ROUNDED, border_style="red"))
