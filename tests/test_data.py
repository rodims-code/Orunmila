"""Tests de data.py : on vérifie le nettoyage sur un mini-fichier fabriqué à la main."""

import numpy as np
import pandas as pd

from orunmila.data import clean_season
from orunmila.metrics import evaluate_odds_source


def make_raw() -> pd.DataFrame:
    """Imite un CSV de football-data.co.uk : dates mixtes, une ligne vide, pas de colonnes Avg."""
    return pd.DataFrame(
        {
            "Div": ["E0", "E0", "E0", None],
            "Date": ["16/08/2019", "17/08/19", "18/08/2019", None],
            "HomeTeam": [" Liverpool", "West Ham", "Chelsea", None],
            "AwayTeam": ["Norwich", "Man City", "Arsenal", None],
            "FTHG": [4, 0, 2, np.nan],
            "FTAG": [1, 5, 2, np.nan],
            "PSH": [1.14, 12.0, 1.0, np.nan],  # 1.0 = cote impossible, doit devenir NaN
            "PSD": [9.0, 7.0, 3.4, np.nan],
            "PSA": [21.0, 1.25, 3.3, np.nan],
        }
    )


def test_blank_rows_are_dropped():
    assert len(clean_season(make_raw(), "1920")) == 3


def test_mixed_date_formats_are_parsed():
    df = clean_season(make_raw(), "1920")
    assert df["date"].iloc[0] == pd.Timestamp("2019-08-16")
    assert df["date"].iloc[1] == pd.Timestamp("2019-08-17")


def test_team_names_are_stripped():
    assert clean_season(make_raw(), "1920")["home"].iloc[0] == "Liverpool"


def test_result_is_computed_from_goals():
    df = clean_season(make_raw(), "1920")
    assert list(df["result"]) == ["H", "A", "D"]
    assert pd.api.types.is_integer_dtype(df["home_goals"])


def test_missing_odds_source_becomes_nan():
    df = clean_season(make_raw(), "1920")
    assert df["avg_h"].isna().all()
    assert df["pin_h"].iloc[0] == 1.14


def test_impossible_odds_become_nan():
    df = clean_season(make_raw(), "1920")
    assert np.isnan(df["pin_h"].iloc[2])


def test_bookmaker_evaluation_skips_missing_source():
    df = clean_season(make_raw(), "1920")
    assert evaluate_odds_source(df, "avg") is None
    result = evaluate_odds_source(df, "pin")
    assert result["matches"] == 2  # la ligne à cote impossible est ignorée
