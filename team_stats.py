import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output, callback

# Charger les données depuis Excel
file_path = "data/L1QC.xlsx"
df_matchs = pd.read_excel(file_path, sheet_name="matchs")
df_teams = pd.read_excel(file_path, sheet_name="teams")  # Charger les noms des équipes

# Associer les noms des équipes aux stats
df_matchs = df_matchs.merge(df_teams[['id', 'name']], left_on='team_id', right_on='id', how='left')

# Calculer la possession
df_matchs['possession'] = (
    df_matchs['passes_bwd_successful'] + df_matchs['passes_fwd_successful'] +
    df_matchs['passes_left_successful'] + df_matchs['passes_right_successful']
) / (
    df_matchs['passes_right'] + df_matchs['passes_fwd'] +
    df_matchs['passes_bwd'] + df_matchs['passes_left']
)

# Nettoyer la colonne 'goals_for'
def count_goals(goals_str):
    if isinstance(goals_str, str):
        return len(goals_str.split(";"))
    return 0

df_matchs['goals_for'] = df_matchs['goals_for'].apply(count_goals)

# Fonction pour compter les cartons dans les colonnes `yellow_cards_for` et `red_cards_for`
def count_cards(card_str):
    if isinstance(card_str, str):
        return len(card_str.split(";"))
    return 0

df_matchs['yellow_cards_for'] = df_matchs['yellow_cards_for'].apply(count_cards)
df_matchs['red_cards_for'] = df_matchs['red_cards_for'].apply(count_cards)

# Ajouter la colonne `total_cards`
df_matchs['total_cards'] = df_matchs['yellow_cards_for'] + df_matchs['red_cards_for']

# Convertir les colonnes en nombres
numeric_columns = ['shots', 'goals_for', 'possession', 'fouls_committed',
                   'yellow_cards_for', 'red_cards_for', 'tackles_committed', 'goals_against',
                   'total_cards', 'passes_fwd', 'passes_bwd', 'aerial_challenges', 'aerial_challenges_successful']

for col in numeric_columns:
    df_matchs[col] = pd.to_numeric(df_matchs[col], errors='coerce')
    df_matchs[col] = df_matchs[col].fillna(0)

# Agréger les statistiques par équipe
df_team_stats = df_matchs.groupby(['team_id', 'name']).agg({
    'shots': 'sum',
    'goals_for': 'sum',
    'possession': 'mean',
    'fouls_committed': 'sum',
    'yellow_cards_for': 'sum',
    'red_cards_for': 'sum',
    'tackles_committed': 'sum',
    'goals_against': 'sum',
    'total_cards': 'sum',
    'passes_fwd': 'sum',
    'passes_bwd': 'sum',
    'aerial_challenges': 'sum',
    'aerial_challenges_successful': 'sum'
}).reset_index()

# Convertir team_id en int
df_team_stats['team_id'] = df_team_stats['team_id'].astype(int)

# Liste des équipes pour le menu déroulant
team_options = [{'label': "Aucune sélection", 'value': None}] + [
    {'label': name, 'value': int(team_id)} for team_id, name in zip(df_team_stats['team_id'], df_team_stats['name'])
]

# Liste des types de statistiques (Offensif / Défensif / Possession)
stat_types = [
    {'label': "Offensif", 'value': "offensif"},
    {'label': "Défensif", 'value': "defensif"},
    {'label': "Possession", 'value': "possession"}
]

# Contenu de l'onglet Team Stats
layout = html.Div([
    html.Div([
        html.H3("Statistiques des Équipes", style={'display': 'inline-block', 'margin-right': '20px'}),

        dcc.Dropdown(
            id="stat-type-dropdown",
            options=stat_types,
            value="offensif",
            clearable=False,
            style={'width': '200px', 'display': 'inline-block', 'verticalAlign': 'middle'}
        ),

        dcc.Dropdown(
            id="team-dropdown",
            options=team_options,
            placeholder="Sélectionnez une équipe",
            value=None,
            clearable=True,
            searchable=True,
            style={'width': '300px', 'display': 'inline-block', 'verticalAlign': 'middle'}
        ),

        dcc.Checklist(
            id="toggle-names",
            options=[{"label": "👁 Afficher les noms des équipes", "value": "show"}],
            value=["show"],  # Par défaut, les noms sont affichés
            style={'margin-left': '20px', 'margin-bottom': '10px'}
        )
    ], style={'display': 'flex', 'alignItems': 'center'}),

    html.Div([
        dcc.Graph(id="scatter-graph-1", style={'width': '48%', 'display': 'inline-block'}),
        dcc.Graph(id="scatter-graph-2", style={'width': '48%', 'display': 'inline-block'})
    ])
])

# Callback pour mettre à jour les graphiques dynamiquement
@callback(
    [Output("scatter-graph-1", "figure"), Output("scatter-graph-2", "figure")],
    [Input("team-dropdown", "value"), Input("stat-type-dropdown", "value"), Input("toggle-names", "value")]
)
def update_graphs(selected_team, stat_type, show_names):
    show_text = "show" in show_names
    # Convertir l'équipe sélectionnée en int
    if selected_team is not None:
        try:
            selected_team = int(selected_team)
        except ValueError:
            selected_team = None

    # Gérer le cas où aucune équipe n'est sélectionnée
    df_team_stats["highlight"] = df_team_stats["team_id"] == selected_team if selected_team is not None else False

    if stat_type == "offensif":
        graph_1 = px.scatter(df_team_stats, x="shots", y="goals_for",
                             color=df_team_stats["highlight"].map({True: "red", False: "blue"}),
                             text=df_team_stats["name"] if show_text else None,
                             title="Relation entre tirs et buts marqués",
                             labels={"shots": "Nombre total de tirs", "goals_for": "Nombre de buts marqués"},
                             hover_data=["name", "shots", "goals_for"])

        graph_2 = px.scatter(df_team_stats, x="possession", y="goals_for",
                             color=df_team_stats["highlight"].map({True: "red", False: "blue"}),
                             title="Relation entre possession et buts marqués",
                             labels={"possession": "Pourcentage de possession", "goals_for": "Nombre de buts marqués"},
                             hover_data=["name", "possession", "goals_for"])

    elif stat_type == "defensif":
        graph_1 = px.scatter(df_team_stats, x="fouls_committed", y="total_cards",
                             color=df_team_stats["highlight"].map({True: "red", False: "blue"}),
                             text=df_team_stats["name"] if show_text else None,
                             title="Fautes commises vs Nombre total de cartons",
                             labels={"fouls_committed": "Nombre de fautes", "total_cards": "Total des cartons"},
                             hover_data=["name", "fouls_committed", "yellow_cards_for", "red_cards_for"])

        graph_2 = px.scatter(df_team_stats, x="tackles_committed", y="goals_against",
                             color=df_team_stats["highlight"].map({True: "red", False: "blue"}),
                             text=df_team_stats["name"] if show_text else None,
                             title="Tacles réalisés vs Buts concédés",
                             labels={"tackles_committed": "Total des tacles", "goals_against": "Buts concédés"},
                             hover_data=["name", "tackles_committed", "goals_against"])

    else:
        graph_1 = px.scatter(df_team_stats, x="passes_fwd", y="passes_bwd",
                             color=df_team_stats["highlight"].map({True: "red", False: "blue"}),
                             text=df_team_stats["name"] if show_text else None,
                             title="Passes en avant vs Passes en retrait",
                             labels={"passes_fwd": "Passes en avant", "passes_bwd": "Passes en retrait"},
                             hover_data=["name", "passes_fwd", "passes_bwd"])

        graph_2 = px.scatter(df_team_stats, x="aerial_challenges", y="aerial_challenges_successful",
                             color=df_team_stats["highlight"].map({True: "red", False: "blue"}),
                             text=df_team_stats["name"] if show_text else None,
                             title="Duels aériens remportés vs Duels aériens totaux",
                             labels={"aerial_challenges": "Duels aériens", "aerial_challenges_successful": "Duels gagnés"},
                             hover_data=["name", "aerial_challenges", "aerial_challenges_successful"])

    return graph_1, graph_2
