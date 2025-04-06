# matchs.py

import pandas as pd
from dash import html, dash_table
from dash import dcc, Input, Output
from dash import callback

# Charger les données
file_path = "data/L1QC.xlsx"  # Mets le chemin correct si besoin
df_matchs = pd.read_excel(file_path, sheet_name="matchs")
df_teams = pd.read_excel(file_path, sheet_name="teams")

# Filtrer les équipes masculines
equipes_masculines = df_teams[df_teams["name"].str.endswith("M")]
masculine_team_ids = set(equipes_masculines["id"])

# Garder uniquement les matchs entre équipes masculines
df_matchs_masculins = df_matchs[
    (df_matchs["team_id"].isin(masculine_team_ids)) &
    (df_matchs["team_away_id"].isin(masculine_team_ids))
]

# Ajouter les noms des équipes
df_matchs_masculins = df_matchs_masculins.merge(
    equipes_masculines[["id", "name"]],
    how="left", left_on="team_id", right_on="id"
).rename(columns={"name": "home_team"})

df_matchs_masculins = df_matchs_masculins.merge(
    equipes_masculines[["id", "name"]],
    how="left", left_on="team_away_id", right_on="id"
).rename(columns={"name": "away_team"})

# === TRAITEMENT DES SCORES === #

def compter_buts_for(chaine):
    if pd.isna(chaine) or str(chaine) == "-1":
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
    df_matchs_masculins["home_team"] + " " +
    df_matchs_masculins["home_goals"].astype(str) + " - " +
    df_matchs_masculins["away_goals"].astype(str) + " " +
    df_matchs_masculins["away_team"]
)
#Game day
def rebuild_game_days(df):
    
    # Copier pour ne pas modifier le DataFrame original
    df_temp = df.copy()

    # Modifier temporairement la date d’un match précis
    df_temp.loc[(df_temp["home_team"] == "AS BLAINVILLE M") & (df_temp["away_team"] == "CELTIX DU HAUT-RICHELIEU M"), "date"] = pd.to_datetime(2024-8-11)

    # Trier et reconstruire les journées
    df_temp = df_temp.sort_values(by="date").reset_index(drop=True)
    df_temp["game_day_new"] = df_temp.index // 5 + 1

    # Recalculer les scores affichés si besoin
    df_temp["score"] = (
        df_temp["home_team"] + " " +
        df_temp["home_goals"].astype(str) + " - " +
        df_temp["away_goals"].astype(str) + " " +
        df_temp["away_team"]
    )

    # Garder les colonnes utiles
    return df_temp[["game_day_new", "date", "home_team", "away_team", "score"]]



# Sélectionner les colonnes utiles et trier par date décroissante
df_resultats = rebuild_game_days(df_matchs_masculins)
df_resultats = df_resultats.sort_values(by="game_day_new", ascending=False)

# === DASH LAYOUT === #

layout = html.Div([
    html.H3("scores des matchs masculins par journée (reconstruite)"),

    # Dropdown de sélection d'équipe
    dcc.Dropdown(
        id='equipe-filter',
        options=[
            {'label': equipe, 'value': equipe}
            for equipe in sorted(set(df_matchs_masculins["home_team"]) | set(df_matchs_masculins["away_team"]))
        ],
        placeholder="Choisir une équipe",
        style={'marginBottom': '20px'}
    ),

    # Contenu de la table (rempli par le callback dans app.py)
    html.Div(id="filtered-table")
])

