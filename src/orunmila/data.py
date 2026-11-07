"""Données : télécharger, nettoyer, fusionner (Phase 1).

CE QUE FAIT CE FICHIER, EN 4 ÉTAPES
-----------------------------------
1. TÉLÉCHARGER un fichier CSV par saison depuis football-data.co.uk
   et le ranger tel quel dans data/raw/ (on ne le modifie jamais).
2. NETTOYER chaque saison : noms de colonnes clairs, dates lisibles,
   buts en nombres entiers, cotes en nombres, lignes vides supprimées.
3. FUSIONNER toutes les saisons dans un seul tableau trié par date.
4. SAUVEGARDER le résultat dans data/processed/premier_league.csv.

CODE DES SAISONS : "2324" = saison 2023-2024, "2425" = 2024-2025, etc.

COLONNES DU TABLEAU FINAL
-------------------------
season, date, home (équipe à domicile), away (équipe à l'extérieur),
home_goals, away_goals, result (H = victoire domicile, D = nul, A = victoire extérieur)
+ 3 cotes (h, d, a) pour chaque source, quand elles existent :
    pin_*  = Pinnacle (bookmaker de référence, très précis)
    avg_*  = moyenne du marché
    b365_* = Bet365
Si une source n'existe pas pour une saison, ses cotes sont vides (NaN).
"""

from pathlib import Path

import numpy as np
import pandas as pd
import requests

# --- Chemins : calculés depuis l'emplacement de ce fichier -------------
# data.py est dans  Orunmila/src/orunmila/data.py
# parents[0] = orunmila, parents[1] = src, parents[2] = Orunmila (racine)
ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
PROCESSED_FILE = PROCESSED_DIR / "premier_league.csv"

# --- Réglages ----------------------------------------------------------
LEAGUE = "E0"  # E0 = Premier League
BASE_URL = "https://www.football-data.co.uk/mmz4281/{season}/{league}.csv"
# 2019-20 -> 2025-26 : les cotes "moyenne du marché" existent depuis 2019-20.
DEFAULT_SEASONS = ["1920", "2021", "2122", "2223", "2324", "2425", "2526"]

# Pour chaque source de cotes, les noms de colonnes possibles dans les CSV
# (ils ont changé au fil des années, donc on essaie plusieurs variantes).
ODDS_SOURCES = {
    "pin": [("PSH", "PSD", "PSA"), ("PH", "PD", "PA")],
    "avg": [("AvgH", "AvgD", "AvgA"), ("BbAvH", "BbAvD", "BbAvA")],
    "b365": [("B365H", "B365D", "B365A")],
}


# ======================================================================
# Étape 1 : télécharger
# ======================================================================
def download_season(season: str, league: str = LEAGUE, force: bool = False) -> Path | None:
    """Télécharge une saison dans data/raw/. Renvoie le chemin, ou None si échec.

    Si le fichier est déjà là, on ne le retélécharge pas (sauf force=True).
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{league}_{season}.csv"
    if path.exists() and not force:
        return path

    url = BASE_URL.format(season=season, league=league)
    try:
        response = requests.get(url, timeout=30, headers={"User-Agent": "Orunmila/0.1 (projet perso)"})
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"  [!] Saison {season} : téléchargement impossible ({error})")
        return None

    path.write_bytes(response.content)
    return path


def read_raw_csv(path: Path) -> pd.DataFrame:
    """Lit un CSV brut. Certains fichiers sont en latin-1, d'autres en utf-8."""
    try:
        return pd.read_csv(path, encoding="utf-8-sig", on_bad_lines="skip")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin-1", on_bad_lines="skip")


# ======================================================================
# Étape 2 : nettoyer une saison
# ======================================================================
def _find_odds_columns(df: pd.DataFrame, candidates) -> tuple[str, str, str] | None:
    """Renvoie le premier trio de colonnes de cotes présent dans le fichier."""
    for trio in candidates:
        if all(column in df.columns for column in trio):
            return trio
    return None


def clean_season(raw: pd.DataFrame, season: str) -> pd.DataFrame:
    """Transforme le CSV brut d'une saison en tableau propre."""
    needed = ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"]
    missing = [column for column in needed if column not in raw.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans la saison {season} : {missing}")

    # On supprime les lignes vides ou sans résultat (matchs pas encore joués).
    df = raw.dropna(subset=needed)

    out = pd.DataFrame(
        {
            "season": season,
            # dayfirst=True : les dates sont au format jour/mois/année.
            # format="mixed" : accepte "16/08/2019" ET "16/08/19".
            "date": pd.to_datetime(df["Date"], dayfirst=True, format="mixed"),
            "home": df["HomeTeam"].astype(str).str.strip(),
            "away": df["AwayTeam"].astype(str).str.strip(),
            "home_goals": pd.to_numeric(df["FTHG"]).astype(int),
            "away_goals": pd.to_numeric(df["FTAG"]).astype(int),
        },
        index=df.index,
    )

    # Le résultat est recalculé depuis les buts : impossible d'avoir une incohérence.
    out["result"] = np.select(
        [out["home_goals"] > out["away_goals"], out["home_goals"] < out["away_goals"]],
        ["H", "A"],
        default="D",
    )

    # Cotes : une source après l'autre. Absente -> NaN (case vide).
    for prefix, candidates in ODDS_SOURCES.items():
        trio = _find_odds_columns(df, candidates)
        for letter, position in (("h", 0), ("d", 1), ("a", 2)):
            name = f"{prefix}_{letter}"
            if trio is None:
                out[name] = np.nan
            else:
                odds = pd.to_numeric(df[trio[position]], errors="coerce")
                out[name] = odds.where(odds > 1.0)  # une cote <= 1,00 n'a pas de sens

    return out.reset_index(drop=True)


# ======================================================================
# Étape 3 : fusionner toutes les saisons
# ======================================================================
def build_dataset(seasons: list[str] | None = None, force: bool = False) -> pd.DataFrame:
    """Télécharge + nettoie + fusionne les saisons demandées."""
    seasons = seasons or DEFAULT_SEASONS
    frames = []
    for season in seasons:
        print(f"Saison {season} ...")
        path = download_season(season, force=force)
        if path is None:
            continue
        frames.append(clean_season(read_raw_csv(path), season))

    if not frames:
        raise RuntimeError("Aucune saison n'a pu être chargée. Vérifie ta connexion internet.")

    df = pd.concat(frames, ignore_index=True)
    df = df.sort_values(["date", "home"], kind="stable")  # ordre chronologique
    df = df.drop_duplicates(subset=["date", "home", "away"])
    return df.reset_index(drop=True)


def quality_report(df: pd.DataFrame) -> dict:
    """Les vérifications demandées par la Phase 1 (doublons, trous, cohérence)."""
    return {
        "matches": len(df),
        "seasons": int(df["season"].nunique()),
        "teams": len(set(df["home"]) | set(df["away"])),
        "date_min": df["date"].min().date(),
        "date_max": df["date"].max().date(),
        "duplicates": int(df.duplicated(subset=["date", "home", "away"]).sum()),
        "matches_per_season": df.groupby("season").size().to_dict(),
        "odds_coverage": {prefix: float(df[f"{prefix}_h"].notna().mean()) for prefix in ODDS_SOURCES},
    }


# ======================================================================
# Étape 4 : sauvegarder / recharger
# ======================================================================
def save_dataset(df: pd.DataFrame) -> Path:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_FILE, index=False)
    return PROCESSED_FILE


def load_dataset() -> pd.DataFrame:
    if not PROCESSED_FILE.exists():
        raise FileNotFoundError("Données introuvables. Lance d'abord :  python -m orunmila download")
    return pd.read_csv(PROCESSED_FILE, parse_dates=["date"])
