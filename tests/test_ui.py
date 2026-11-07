"""Tests pour le module d'interface ui.py."""

from pathlib import Path
from orunmila import ui


def test_ui_plain_mode_toggle():
    ui.set_plain(True)
    assert ui.is_plain() is True
    ui.set_plain(False)
    assert ui.is_plain() is False


def test_ui_print_info_does_not_crash(capsys):
    ui.set_plain(True)
    ui.print_info("0.1.0", "Phase 3 (Modèle v1 Poisson)", Path("data/processed/dummy.csv"), False)
    captured = capsys.readouterr()
    assert "Orunmila v0.1.0" in captured.out
    assert "Phase 3" in captured.out

    ui.set_plain(False)
    ui.print_info("0.1.0", "Phase 3 (Modèle v1 Poisson)", Path("data/processed/dummy.csv"), True)


def test_ui_print_baseline_plain(capsys):
    ui.set_plain(True)
    rows = [
        {"label": "Pinnacle", "matches": 1000, "margin": 0.025, "log_loss": 0.9623, "brier": 0.58},
    ]
    ui.print_baseline_results(1000, rows, {"pin": "Pinnacle"})
    captured = capsys.readouterr()
    assert "Pinnacle" in captured.out
    assert "0.9623" in captured.out
    ui.set_plain(False)
