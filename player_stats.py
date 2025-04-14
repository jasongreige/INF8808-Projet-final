# ====================================================== PREPROCESS ====================================================== #

import pandas as pd


# Charger les données depuis Excel
file_path = "assets\data\L1QC.xlsx"
df_players = pd.read_excel(file_path, sheet_name="players")
df_players_season = pd.read_excel(file_path, sheet_name="players_season")
df_players_game = pd.read_excel(file_path, sheet_name="players_game")
df_teams = pd.read_excel(file_path, sheet_name="teams")

# Associer les noms et prénoms des joueurs à leurs stats
df_players_game = df_players_game.merge(df_players[['id', 'first_name', 'last_name']], left_on='player_id', right_on='id', how='left')

# Associer les saisons aux stats des joueurs
df_players_game = df_players_game.merge(df_players_season[['id', 'season']], left_on='player_season_id', right_on='id', how='left')

# Associer les noms d'équipe aux stats des joueurs
df_players_season = df_players_season.merge(df_teams[['id', 'name']], left_on='team_id', right_on='id', how='left')


# Afficher les colonnes pour vérifier
print(df_players_game.columns)
print(df_players_season.columns)

# Supprimer les colonnes inutiles
if 'id_y' in df_players_game.columns:
    df_players_game.drop(columns=['id_y'], inplace=True)
if 'id' in df_players_game.columns:
    df_players_game.drop(columns=['id'], inplace=True)
df_players_game.rename(columns={'id_x': 'id'}, inplace=True)

if 'id_y' in df_players_season.columns:
    df_players_season.drop(columns=['id_y'], inplace=True)
if 'id' in df_players_season.columns:
    df_players_season.drop(columns=['id'], inplace=True)
df_players_season.rename(columns={'id_x': 'id'}, inplace=True)


# Supprimer les lignes où first_name et last_name sont NaN
df_players_game_cleaned = df_players_game.dropna(subset=['first_name', 'last_name'])

# ================= Statistiques offensives =================
df_offensive_stats = df_players_game_cleaned[['season', 'player_id', 'first_name', 'last_name', 'position_played', 
                                              'goals', 'assists', 'scnd_assists', 'passes_backward', 'passes_forward', 
                                              'passes_left', 'passes_right', 'passes_successful', 'shots_successful', 
                                              'shots_total', 'penalties_successful', 'penalties_total', 
                                              'dribbles_successful', 'dribbles_total', 'starter',
                                              'offensive_challenges_successful','offensive_challenges']].copy()

df_offensive_stats['first_name'] = df_offensive_stats['first_name'].astype(str)
df_offensive_stats['last_name'] = df_offensive_stats['last_name'].astype(str)

df_offensive_stats['player'] = df_offensive_stats['first_name'] + ' ' + df_offensive_stats['last_name']
df_offensive_stats['number_of_starting'] = df_offensive_stats['starter']
df_offensive_stats['goals_and_assists'] = df_offensive_stats['goals'] + df_offensive_stats['assists'] + df_offensive_stats['scnd_assists']
df_offensive_stats['passes_total'] = df_offensive_stats['passes_backward'] + df_offensive_stats['passes_forward'] + df_offensive_stats['passes_left'] + df_offensive_stats['passes_right']
df_offensive_stats['precision_passes_(%)'] = (df_offensive_stats['passes_successful'] / df_offensive_stats['passes_total']).fillna(0) * 100
df_offensive_stats['precision_shots_(%)'] = (df_offensive_stats['shots_successful'] / df_offensive_stats['shots_total']).fillna(0) * 100
df_offensive_stats['precision_dribbles_(%)'] = (df_offensive_stats['dribbles_successful'] / df_offensive_stats['dribbles_total']).fillna(0) * 100
df_offensive_stats['challenges_(%)'] = (df_offensive_stats['offensive_challenges_successful'] / df_offensive_stats['offensive_challenges']).fillna(0) * 100

df_offensive_stats = df_offensive_stats.groupby(['player_id'], as_index=False).agg({
    'season': lambda x: ', '.join(map(str, x.unique())),
    'player': lambda x: x.iloc[0],
    'position_played': lambda x: x.iloc[0],
    'number_of_starting': sum,
    'shots_total': sum,
    'goals_and_assists': sum,
    'passes_total': sum,
    'precision_passes_(%)': lambda x: round(x.mean(), 2),
    'precision_shots_(%)': lambda x: round(x.mean(), 2),
    'precision_dribbles_(%)': lambda x: round(x.mean(), 2),
    'challenges_(%)': lambda x: round(x.mean(), 2)
})

# ================= Statistiques défensives =================
df_defensive_stats = df_players_game_cleaned[['season', 'player_id', 'first_name', 'last_name', 'position_played', 
                                              'fouls_committed', 'yellow_cards', 'red_cards','tackles_successful', 
                                              'tackles_total', 'aerial_challenges_successful','aerial_challenges', 
                                              'shots_blocked','defensive_challenges_successful','defensive_challenges', 
                                              'clearances_successful', 'clearances', 'starter', 'recup_interception_ball_position', 
                                              'recup_challenge_ball_position', 'recup_no_intervention_ball_position']].copy()

df_defensive_stats['first_name'] = df_defensive_stats['first_name'].astype(str)
df_defensive_stats['last_name'] = df_defensive_stats['last_name'].astype(str)

# Fonction pour compter le nombre d'interceptions dans les colonnes associées
def sum_column_values(column):
    values = list(map(int,column.split(',')))
    return sum(values)

df_defensive_stats['recup_interception_ball_position'] = df_defensive_stats['recup_interception_ball_position'].apply(sum_column_values)
df_defensive_stats['recup_challenge_ball_position'] = df_defensive_stats['recup_challenge_ball_position'].apply(sum_column_values)
df_defensive_stats['recup_no_intervention_ball_position'] = df_defensive_stats['recup_no_intervention_ball_position'].apply(sum_column_values)

df_defensive_stats['player'] = df_defensive_stats['first_name'] + " " + df_defensive_stats['last_name']
df_defensive_stats['number_of_starting'] = df_defensive_stats['starter']
df_defensive_stats['challenges_(%)'] = (df_defensive_stats['defensive_challenges_successful'] / df_defensive_stats['defensive_challenges']).fillna(0) * 100
df_defensive_stats['tackles_(%)'] = (df_defensive_stats['tackles_successful'] / df_defensive_stats['tackles_total']).fillna(0) * 100
df_defensive_stats['aerial_challenges_(%)'] = (df_defensive_stats['aerial_challenges_successful'] / df_defensive_stats['aerial_challenges']).fillna(0) * 100
df_defensive_stats['clearances_(%)'] = (df_defensive_stats['clearances_successful'] / df_defensive_stats['clearances']).fillna(0) * 100
df_defensive_stats['total_interceptions'] = df_defensive_stats[['recup_interception_ball_position', 
                                                                'recup_challenge_ball_position', 
                                                                'recup_no_intervention_ball_position']].sum(axis=1)

df_defensive_stats = df_defensive_stats.groupby(['player_id'], as_index=False).agg({
    "season": lambda x: ', '.join(map(str,x.unique())),
    "player": lambda x: x.iloc[0],
    "position_played": lambda x: x.iloc[0],
    "number_of_starting": sum,
    "fouls_committed": sum,
    "yellow_cards": sum,
    "red_cards": sum,
    "total_interceptions": sum,
    "shots_blocked": sum,
    "challenges_(%)": lambda x: round(x.mean(),2),
    "tackles_(%)": lambda x: round(x.mean(),2),
    "aerial_challenges_(%)": lambda x: round(x.mean(),2),
    "clearances_(%)": lambda x: round(x.mean(),2)
})

# ================= Statistiques de gardien =================
df_goalkeeper_stats = df_players_game_cleaned[['season', 'player_id', 'first_name', 'last_name', 'position_played',  
                                              'starter', 'gk_clearances_successful','gk_clearances']].copy()

df_goalkeeper_stats['first_name'] = df_goalkeeper_stats['first_name'].astype(str)
df_goalkeeper_stats['last_name'] = df_goalkeeper_stats['last_name'].astype(str)

df_goalkeeper_stats['player'] = df_goalkeeper_stats['first_name'] + ' ' + df_goalkeeper_stats['last_name']
df_goalkeeper_stats['number_of_starting'] = df_goalkeeper_stats['starter']
df_goalkeeper_stats['gk_clearances_(%)'] = (df_goalkeeper_stats['gk_clearances_successful'] / df_goalkeeper_stats['gk_clearances']).fillna(0) * 100


df_goalkeeper_stats = df_goalkeeper_stats[df_goalkeeper_stats['position_played'] == 'Goalkeeper']

df_goalkeeper_stats = df_goalkeeper_stats.groupby(['player_id'], as_index=False).agg({
    'season': lambda x: ', '.join(map(str, x.unique())),
    'first_name': lambda x: x.iloc[0],
    'last_name': lambda x: x.iloc[0],
    'position_played': lambda x: x.iloc[0],
    'number_of_starting': sum,
    'gk_clearances_(%)': lambda x: round(x.mean(), 2)
})

df_goalkeeper_stats['player'] = df_goalkeeper_stats['first_name'] + ' ' + df_goalkeeper_stats['last_name']

df_goalkeeper_stats = df_goalkeeper_stats[['player_id', 
                                           'season', 
                                           'player', 
                                           'number_of_starting',
                                           'gk_clearances_(%)']]

# ================= Statistiques générales =================
df_general_stats_game = df_players_game_cleaned[['season', 'player_id', 'first_name', 'last_name','position_played', 'starter','minutes_played']].copy()

df_general_stats_season = df_players_season[['player_id', 'name']].copy()

df_general_stats = df_general_stats_game.merge(df_general_stats_season, on='player_id', how='left')

df_general_stats['first_name'] = df_general_stats['first_name'].astype(str)
df_general_stats['last_name'] = df_general_stats['last_name'].astype(str)

df_general_stats = df_general_stats.groupby(['player_id'], as_index=False).agg({
    'season': lambda x: ', '.join(map(str, x.unique())),
    'first_name': lambda x: x.iloc[0],
    'last_name': lambda x: x.iloc[0],
    'position_played': lambda x: x.iloc[0],
    'starter': sum,
    'minutes_played': sum,
    'name': lambda x: x.iloc[0]
})

df_general_stats['player'] = df_general_stats['first_name'] + ' ' + df_general_stats['last_name']
df_general_stats['number_of_starting'] = df_general_stats['starter']
df_general_stats['total_minutes'] = df_general_stats['minutes_played']

df_general_stats = df_general_stats.merge(df_offensive_stats[['player_id', 
                                                              'goals_and_assists', 
                                                              'shots_total', 
                                                              'passes_total', 
                                                              'number_of_starting']], 
                                          on='player_id', how='left')

df_general_stats = df_general_stats.merge(df_defensive_stats[['player_id', 
                                                              'total_interceptions',
                                                              'yellow_cards',
                                                              'red_cards',
                                                              'number_of_starting']], 
                                          on='player_id', how='left')

df_general_stats = df_general_stats[['player_id',
                                     'season',
                                     'player',
                                     'position_played',
                                     'name',
                                     'number_of_starting_x',
                                     'total_minutes',
                                     'goals_and_assists',
                                     'shots_total',
                                     'passes_total',
                                     'total_interceptions',
                                     'yellow_cards',
                                     'red_cards' ]]

df_general_stats.rename(columns={'name': 'team', 'number_of_starting_x': 'number_of_starting'}, inplace=True)

# ====================================================== HISTOGRAMMES ====================================================== #

import plotly.graph_objects as go
import pandas as pd

# Charger les données
df_offensive_stats = pd.read_excel('df_offensive_stats.xlsx')
df_defensive_stats = pd.read_excel('df_defensive_stats.xlsx')
df_goalkeeper_stats = pd.read_excel('df_goalkeeper_stats.xlsx')
df_general_stats = pd.read_excel('df_general_stats.xlsx')

def create_histogram(df, column, player_id, title, unit):
    player_data = df[df['player_id'] == player_id]
    if player_data.empty:
        print(f"Erreur : Le joueur avec l'ID {player_id} n'a pas été trouvé dans les données.")
        return go.Figure()
    
    player_stat = player_data[column].values[0]
    player_name = player_data['player'].values[0]
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=df[column], name='Autres joueurs'))
    fig.add_trace(go.Scatter(
        x=[player_stat], 
        y=[0], 
        mode='markers', 
        marker=dict(color='red', size=10), 
        name=player_name,
        hovertext=f"{player_name}<br>{player_stat} {unit}",
        hoverinfo="text"
    ))
    fig.update_layout(
        title=title,
        yaxis_title='Nombre de joueurs',
        xaxis=dict(range=[df[column].min(), df[column].max()], fixedrange=True),
        yaxis=dict(fixedrange=True),
        xaxis_title=None  # Supprimer le titre de l'axe des abscisses
    )
    return fig

def create_offensive_histograms(player_id):
    histograms = []
    histograms.append(create_histogram(df_offensive_stats, 'goals_and_assists', player_id, 'Distribution des buts et passes décisives', 'B et P/D'))
    histograms.append(create_histogram(df_offensive_stats, 'passes_total', player_id, 'Distribution des passes totales', 'passes'))
    histograms.append(create_histogram(df_offensive_stats, 'precision_dribbles_(%)', player_id, 'Distribution des précisions de dribbles (%)', '%'))
    histograms.append(create_histogram(df_offensive_stats, 'challenges_(%)', player_id, 'Distribution du % des challenges offensifs (%)', '%'))
    return histograms

def create_defensive_histograms(player_id):
    histograms = []
    histograms.append(create_histogram(df_defensive_stats, 'tackles_(%)', player_id, 'Distribution du % des tacles', '%'))
    histograms.append(create_histogram(df_defensive_stats, 'challenges_(%)', player_id, 'Distribution du % des challenges défensifs', '%'))
    histograms.append(create_histogram(df_defensive_stats, 'total_interceptions', player_id, 'Distribution du nombre total d\'interceptions', 'titularisations'))
    histograms.append(create_histogram(df_defensive_stats, 'aerial_challenges_(%)', player_id, 'Distribution du % des challenges aériens défensifs (%)', '%'))
    return histograms

def create_goalkeeper_histograms(player_id):
    histograms = []
    histograms.append(create_histogram(df_goalkeeper_stats, 'gk_clearances_(%)', player_id, 'Distribution du % des dégagements', '%'))
    return histograms

def create_general_histograms(player_id):
    histograms = []
    histograms.append(create_histogram(df_general_stats, 'total_minutes', player_id, 'Distribution du nombre total de minutes jouées', 'minutes'))
    histograms.append(create_histogram(df_general_stats, 'goals_and_assists', player_id, 'Distribution du nombre de buts + passes décisives', 'B et P/D'))
    histograms.append(create_histogram(df_general_stats, 'number_of_starting', player_id, 'Distribution du nombre total de titularisations', 'titularisations'))
    histograms.append(create_histogram(df_general_stats, 'total_interceptions', player_id, 'Distribution du nombre total d\'interceptions', 'interceptions'))
    return histograms

# ====================================================== MODES ====================================================== #

MODES = {
    'attack': {
        'name': 'Attaque',
        'dataframe': 'df_offensive_stats',
        'histograms': [
            {'column': 'goals_and_assists', 'title': 'Distribution des buts + passes décisives'},
            {'column': 'passes_total', 'title': 'Distribution des passes totales'},
            {'column': 'precision_dribbles_(%)', 'title': 'Distribution des précisions de dribbles (%)'},
            {'column': 'challenges_(%)', 'title': 'Distribution des challenges offensifs (%)'}
        ]
    },
    'defense': {
        'name': 'Défense',
        'dataframe': 'df_defensive_stats',
        'histograms': [
            {'column': 'tackles_(%)', 'title': 'Distribution du % de tacles'},
            {'column': 'challenges_(%)', 'title': 'Distribution du % de challenges défensifs'},
            {'column': 'total_interceptions', 'title': 'Distribution du nombre total d\'interceptions'},
            {'column': 'aerial_challenges_(%)', 'title': 'Distribution des challenges aériens défensifs (%)'}
        ]
    },
    'goalkeeper': {
        'name': 'Gardien',
        'dataframe': 'df_goalkeeper_stats',
        'histograms': [
            {'column': 'gk_clearances_(%)', 'title': 'Distribution du % de dégagements'}
        ]
    },
    'general': {
        'name': 'Général',
        'dataframe': 'df_general_stats',
        'histograms': [
            {'column': 'total_minutes', 'title': 'Distribution du nombre total de minutes jouées'},
            {'column': 'goals_and_assists', 'title': 'Distribution du nombre de buts + passes décisives'},
            {'column': 'number_of_starting', 'title': 'Distribution du nombre total de titularisations'},
            {'column': 'total_interceptions', 'title': 'Distribution du nombre total d\'interceptions'}
        ]
    }
}

# ====================================================== LAYOUT ====================================================== #

import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import plotly.graph_objects as go
from team_stats import layout as team_stats_layout

# Charger les données
df_offensive_stats = pd.read_excel('df_offensive_stats.xlsx')
df_defensive_stats = pd.read_excel('df_defensive_stats.xlsx')
df_goalkeeper_stats = pd.read_excel('df_goalkeeper_stats.xlsx')
df_general_stats = pd.read_excel('df_general_stats.xlsx')

def filter_by_league(df, league):
    if 'team' in df.columns:
        if league == 'masculine':
            return df[df['team'].str[-1] != 'F']
        elif league == 'feminine':
            return df[df['team'].str[-1] == 'F']
    return df

def merge_with_general(df, general_df):
    return pd.merge(df, general_df[['player_id', 'team']], on='player_id', how='left')

# Préparer les options pour les listes déroulantes
mode_options = [
    {'label': MODES['attack']['name'], 'value': 'attack'},
    {'label': MODES['defense']['name'], 'value': 'defense'},
    {'label': MODES['general']['name'], 'value': 'general'},
    {'label': MODES['goalkeeper']['name'], 'value': 'goalkeeper'}
]

league_options = [
    {'label': 'Masculine', 'value': 'masculine'},
    {'label': 'Feminine', 'value': 'feminine'}
]

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # Important pour Flask

# Définition des onglets et de la mise en page
app.layout = html.Div([
    html.H1("Soccer Stats Québec"),
    dcc.Tabs(id="tabs", value="team_stats", children=[
        dcc.Tab(label="Matchs", value="matchs"),
        dcc.Tab(label="Statistiques des Équipes", value="team_stats"),
        dcc.Tab(label="Statistiques des Joueurs", value="player_stats"),
    ]),
    html.Div(id="tabs-content")
])

# Callback pour afficher le bon contenu selon l'onglet sélectionné
@app.callback(
    Output("tabs-content", "children"),
    [Input("tabs", "value")]
)
def update_tab(tab_name):
    if tab_name == "team_stats":
        return team_stats_layout  # On affiche l'onglet Team Stats
    elif tab_name == "player_stats":
        return html.Div([
            dcc.Store(id='stored-player-id'),
            html.H3("Statistiques des Joueurs", style={'font-size': '20px'}),
            html.Div([
                html.Div([
                    html.H3("Mode d'affichage", style={'display': 'inline-block', 'margin-right': '20px'}),
                    dcc.Dropdown(
                        id='mode-dropdown',
                        options=mode_options,
                        value='general',
                        clearable=False,
                        style={'width': '200px', 'display': 'inline-block', 'verticalAlign': 'middle'}
                    )
                ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'middle'}),
                html.Div([
                    html.H3("Ligue", style={'display': 'inline-block', 'margin-right': '20px'}),
                    dcc.Dropdown(
                        id='league-dropdown',
                        options=league_options,
                        value='masculine',
                        clearable=False,
                        style={'width': '200px', 'display': 'inline-block', 'verticalAlign': 'middle'}
                    )
                ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'middle'}),
                html.Div([
                    html.H3("Recherche d'un joueur", style={'display': 'inline-block', 'margin-right': '20px'}),
                    dcc.Input(id='player-search', type='text', placeholder='Saisir le Nom du Joueur', style={'width': '300px', 'display': 'inline-block', 'verticalAlign': 'middle'})
                ], style={'width': '40%', 'display': 'inline-block', 'verticalAlign': 'middle'})
            ], style={'width': '100%', 'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center'}),
            html.Div(id='player-table', style={'width': '100%', 'display': 'inline-block', 'verticalAlign': 'top', 'height': '50vh', 'overflowY': 'scroll'}),
            html.Div([
                html.Div(id='player-info', style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                html.Div(id='player-histograms', style={'width': '70%', 'display': 'inline-block', 'verticalAlign': 'top'})
            ], style={'width': '100%', 'display': 'inline-block', 'verticalAlign': 'top', 'height': '50vh'})
        ])
    elif tab_name == "matchs":
        return html.Div([
            html.H3("Matchs"),
            html.P("Calendrier des matchs à afficher ici...")
        ])
    return html.Div("Sélectionnez un onglet.")

@app.callback(
    Output('player-table', 'children'),
    [Input('mode-dropdown', 'value'), Input('league-dropdown', 'value'), Input('player-search', 'value')],
    [State('stored-player-id', 'data')]
)
def update_table(mode, league, search_value, stored_player_id):
    df = pd.read_excel(f'{MODES[mode]["dataframe"]}.xlsx')
    if mode != 'general':
        df = merge_with_general(df, df_general_stats)
    df = filter_by_league(df, league)
    
    # Renommer les colonnes
    df = df.rename(columns={
        'player_id': 'Matricule',
        'season': 'Saison',
        'player': 'Joueur',
        'position_played': 'Position',
        'number_of_starting': 'Titularisations',
        'team': 'Équipe',
        'total_minutes': 'Temps de jeu (minutes)',
        'goals_and_assists': 'Buts et passes décisives',
        'shots_total': 'Tirs',
        'passes_total': 'Passes',
        'total_interceptions': 'Interceptions',
        'fouls_committed': 'Fautes',
        'yellow_cards': 'Cartons jaune',
        'red_cards': 'Cartons rouge',
        'precision_shots_(%)': 'Réussite tirs (%)',
        'precision_dribbles_(%)': 'Réussite dribbles (%)',
        'challenges_(%)': 'Réussite duels (%)',
        'shots_blocked': 'Tirs bloqués',
        'aerial_challenges_(%)': 'Réussite duels aériens (%)',
        'clearances_(%)': 'Réussite dégagements (%)',
        'tackles_(%)': 'Réussite tacles (%)',
        'gk_clearances_(%)': 'Réussite dégagements (%)'
    })
    
    if search_value:
        df = df[df['Joueur'].str.contains(search_value, case=False, na=False)]
    
    return html.Div([
        html.H3(f'Tableau des statistiques', style={'font-size': '20px'}),
        dash_table.DataTable(
            id='table',
            columns=[{'name': col.replace('_', ' '), 'id': col} for col in df.columns],
            data=df.to_dict('records'),
            style_table={'width': '100%', 'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'whiteSpace': 'normal', 'height': 'auto'},
            row_selectable='single',
            selected_rows=[]
        )
    ], style={'textAlign': 'center', 'width': '100%'})

@app.callback(
    [Output('player-info', 'children'), Output('player-histograms', 'children')],
    [Input('table', 'selected_rows'), Input('mode-dropdown', 'value')],
    [State('table', 'data')]
)
def display_player_info(selected_rows, mode, table_data):
    if not selected_rows:
        return html.Div(), html.Div()
    
    player_index = selected_rows[0]
    df = pd.DataFrame(table_data)
    
    # Assurer que l'index est correctement configuré
    if player_index >= len(df):
        return html.Div(), html.Div()
    
    player_data = df.iloc[player_index]

    # Récupérer l'équipe du joueur à partir du tableau Général si elle n'est pas renseignée
    if mode != 'general' and ('Équipe' not in player_data or pd.isna(player_data['Équipe'])):
        general_df = pd.read_excel('df_general_stats.xlsx')
        general_player_data = general_df[general_df['player_id'] == player_data['Matricule']]
        if not general_player_data.empty:
            player_data['Équipe'] = general_player_data['team'].values[0]

    # Récupérer le poste du joueur à partir du tableau Général si elle n'est pas renseignée
    if mode != 'general' and ('Position' not in player_data or pd.isna(player_data['Position'])):
        general_df = pd.read_excel('df_general_stats.xlsx')
        general_player_data = general_df[general_player_data['player_id'] == player_data['Matricule']]
        if not general_player_data.empty:
            player_data['Position'] = general_player_data['position_played'].values[0]

    player_info = html.Div([
        html.H3("Fiche Joueur"),
        html.P(f"Nom: {player_data.get('Joueur', 'N/A')}"),
        html.P(f"Équipe: {player_data.get('Équipe', 'N/A')}"),
        html.P(f"Poste: {player_data.get('Position', 'N/A')}")
    ])

    histograms = []
    if mode == 'attack':
        histograms = create_offensive_histograms(player_data['Matricule'])
    elif mode == 'defense':
        histograms = create_defensive_histograms(player_data['Matricule'])
    elif mode == 'goalkeeper':
        histograms = create_goalkeeper_histograms(player_data['Matricule'])
    elif mode == 'general':
        histograms = create_general_histograms(player_data['Matricule'])
    else:
        histograms = []  # Pas d'histogrammes pour les modes Masculine et Féminine

    # Créer la mise en page des histogrammes en fonction du nombre d'histogrammes disponibles
    histogram_layout = html.Div([
        html.Div(dcc.Graph(figure=histogram), style={'width': '50%', 'display': 'inline-block'})
        for histogram in histograms
    ], style={'width': '100%', 'display': 'flex', 'flex-wrap': 'wrap'})

    return player_info, histogram_layout