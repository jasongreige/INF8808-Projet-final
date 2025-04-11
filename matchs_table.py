# matchs.py

import pandas as pd
from dash import html, dash_table
from dash import dcc, Input, Output


# Charger les données
file_path = "data/L1QC.xlsx"  # Mets le chemin correct si besoin
df_matchs = pd.read_excel(file_path, sheet_name="matchs")
df_teams = pd.read_excel(file_path, sheet_name="teams")

# Filtrer les équipes masculines
equipes_masculines = df_teams[df_teams["name"].str.endswith("M")]
equipes_masculines = equipes_masculines.rename(columns={"id": "classif_id"})
masculine_team_ids = set(equipes_masculines["classif_id"])

# Garder uniquement les matchs entre équipes masculines
df_matchs_masculins = df_matchs[
    (df_matchs["team_id"].isin(masculine_team_ids)) &
    (df_matchs["team_away_id"].isin(masculine_team_ids))
]
# ========= Tableau des matchs ===========

# Ajouter les noms des équipes
df_matchs_masculins = df_matchs_masculins.merge(
    equipes_masculines[["classif_id", "name"]],
    how="left", left_on="team_id", right_on="classif_id"
).rename(columns={"name": "home_team"})

df_matchs_masculins = df_matchs_masculins.merge(
    equipes_masculines[["classif_id", "name"]],
    how="left", left_on="team_away_id", right_on="classif_id"
).rename(columns={"name": "away_team"})




# === TRAITEMENT DES SCORES === #

def compter_buts_for(chaine):
    if pd.isna(chaine) or str(chaine) in ["-1", "-1,-1"]:
        return 0
    return len(str(chaine).split(";"))

def compter_buts_against(chaine):
    if pd.isna(chaine) or str(chaine) in ["-1", "-1,-1"]:
        return 0
    return len(str(chaine).split(","))

df_matchs_masculins["home_goals"] = df_matchs_masculins["goals_for"].apply(compter_buts_for)
df_matchs_masculins["away_goals"] = df_matchs_masculins["goals_against"].apply(compter_buts_against)

# Colonne score
df_matchs_masculins["score"] = (
    df_matchs_masculins["home_goals"].astype(str) + " - " +
    df_matchs_masculins["away_goals"].astype(str)
)


# Sélectionner les colonnes utiles et trier par date décroissante
df_resultats = df_matchs_masculins[["date", "home_team", "away_team", "score"]]
df_resultats = df_resultats.sort_values(by="date", ascending=False)
df_resultats["match_id"] = df_matchs_masculins["id"]


# ================= Statistiques des matchs =================

df_match_infos = df_matchs_masculins.copy()
# Crée une table des statistiques à partir des identifiants de match
df_match_stats = df_match_infos[["id"]].copy()
df_match_stats.rename(columns={"id": "match_id"}, inplace=True)


# Ajouter les tirs calculés depuis df_match_infos
df_match_stats["shots_home"] = df_match_infos["shots"]
df_match_stats["shots_away"] = df_match_infos["shots_against"]
df_match_stats["shots_on_home"] = df_match_infos["shots_on"]
df_match_stats["shots_on_away"] = df_match_infos["shots_on_against"]

# Ajouter le nombre de passes
df_match_infos["total_passes_home"] = (
    df_match_infos["passes_fwd"].fillna(0) +
    df_match_infos["passes_bwd"].fillna(0) +
    df_match_infos["passes_left"].fillna(0) +
    df_match_infos["passes_right"].fillna(0)
)
df_match_stats["total_passes_home"] = df_match_infos["total_passes_home"]
df_match_stats["total_passes_away"] = df_match_infos["passes_against"]

# Pourcentage de passes
total_passes_both = df_match_infos["total_passes_home"] + df_match_infos["passes_against"]

df_match_infos["possession_home"] = (df_match_infos["total_passes_home"] / total_passes_both * 100).round(1)
df_match_infos["possession_away"] = (df_match_infos["passes_against"] / total_passes_both * 100).round(1)

df_match_stats["possession_home"] = df_match_infos["possession_home"]
df_match_stats["possession_away"] = df_match_infos["possession_away"]

# Autres stats
df_match_stats["offsides_home"] = df_match_infos["offsides"]
df_match_stats["offsides_away"] = df_match_infos["offsides_against"]

df_match_stats["fouls_committed_home"] = df_match_infos["fouls_committed"]
df_match_stats["fouls_committed_away"] = df_match_infos["fouls_sudden"]

df_match_stats["freekicks_home"] = df_match_infos["direct_free_kicks"]
df_match_stats["freekicks_away"] = df_match_infos["direct_free_kicks_against"]

df_match_stats["corners_home"] = df_match_infos["corners"]
df_match_stats["corners_away"] = df_match_infos["corners_against"]



# ============= Frise chronologique ============= #

def safe_split(val, sep=";"):
    val = str(val)
    if val.strip() in ["-1", "-1,-1", "", "dtype: object", "None"]:
        return []
    return val.split(sep)
    
def extract_events_from_match_row(row):
    """
    Extrait tous les événements clés d'un match à partir d'une ligne du DataFrame.
    Renvoie une liste d'événements avec minute, type et équipe.
    """
    events = []

    # === Buts domicile ===
    chaine = row["goals_for"]

    if str(chaine).strip() not in ["-1", "-1,-1", "", "None", "nan"]:
        for entry in str(chaine).split(";"):
            if "," in entry:
                parts = entry.rsplit(",", 1)
                if len(parts) == 2:
                    minute = parts[1].strip()
                    events.append({
                        "minute": minute,
                        "team": "home",
                        "type": "goal"
                    })

    # === Buts extérieur ===
    for minute in safe_split(row["goals_against"], sep=","):
        minute = minute.strip()
        if minute.isdigit():
            events.append({
                "minute": minute,
                "team": "away",
                "type": "goal"
            })

    # === Cartons jaunes ===
    for entry in safe_split(row["yellow_cards_for"]):
        if "," in entry:
            parts = entry.rsplit(",", 1)
            if len(parts) == 2:
                minute = parts[1].strip()
                events.append({
                    "minute": minute,
                    "team": "home",
                    "type": "yellow_card"
                })

    for minute in safe_split(row["yellow_cards_against"]):
        minute = minute.strip()
        if minute.isdigit():
            events.append({
                "minute": minute,
                "team": "away",
                "type": "yellow_card"
            })

    # === Cartons rouges ===
    for entry in safe_split(row["red_cards_for"]):
        if "," in entry:
            parts = entry.rsplit(",", 1)
            if len(parts) == 2:
                minute = parts[1].strip()
                events.append({
                    "minute": minute,
                    "team": "home",
                    "type": "red_card"
                })

    for minute in safe_split(row["red_cards_against"]):
        minute = minute.strip()
        if minute.isdigit():
            events.append({
                "minute": minute,
                "team": "away",
                "type": "red_card"
            })

    # === Remplacements ===
    for entry in safe_split(row["changes_for"]):
        parts = entry.split(",")
        if len(parts) == 3:
            minute = parts[2].strip()
            events.append({
                "minute": minute,
                "team": "home",
                "type": "substitution"
            })

    for entry in safe_split(row["changes_against"]):
        parts = entry.split(",")
        if len(parts) == 3:
            minute = parts[2].strip()
            events.append({
                "minute": minute,
                "team": "away",
                "type": "substitution"
            })
    return events



# === DASH LAYOUT === #

layout = html.Div([
    # Dropdown d'équipe
    dcc.Dropdown(
        id='equipe-filter',
        options=[
            {'label': equipe, 'value': equipe}
            for equipe in sorted(set(df_resultats["home_team"]) | set(df_resultats["away_team"]))
        ],
        placeholder="Choisir une équipe",
        style={'width': '200px', 'display': 'inline-block', 'verticalAlign': 'left', 'marginBottom': '20px'}
    ),

    # Conteneur des deux colonnes côte à côte
    html.Div([
        html.Div(id="filtered-table", style={
            'width': '30%',
            'backgroundColor': '#f9f9f9',
            'padding': '10px',
            'border': '1px solid #ccc',
            'borderRadius': '5px',
            'boxShadow': '2px 2px 4px rgba(0,0,0,0.1)',
            'marginRight': '2%'
        }),
        html.Div(id="match-details", style={
            'width': '68%',
            'backgroundColor': '#f1f1f1',
            'padding': '10px',
            'border': '1px solid #ccc',
            'borderRadius': '5px',
            'boxShadow': '2px 2px 4px rgba(0,0,0,0.1)'
        })
    ], style={
        'display': 'flex',
        'flexWrap': 'nowrap',
        'justifyContent': 'space-between'
    },)
], style={'margin': '0', 'padding': '0'}
)