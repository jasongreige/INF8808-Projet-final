import pandas as pd
from dash import html, dcc, dash_table
import plotly.graph_objects as go
from player_stats import MODES, df_general_stats
from player_stats import (
    create_offensive_histograms,
    create_defensive_histograms,
    create_goalkeeper_histograms,
    create_general_histograms,
    merge_with_general,
    filter_by_league,
    df_general_stats
)

def update_player_table(mode, league, search_value, stored_player_id):
    df = pd.read_excel(f'{MODES[mode]["dataframe"]}.xlsx')
    if mode != 'general':
        df = merge_with_general(df, df_general_stats)
    df = filter_by_league(df, league)
    
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
        'precision_passes_(%)': 'Réussite passes (%)',
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
        html.H3('Tableau des statistiques', style={'font-size': '20px'}),
        dash_table.DataTable(
            id='table',
            columns=[{'name': col, 'id': col} for col in df.columns],
            data=df.to_dict('records'),
            style_table={'width': '100%', 'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'whiteSpace': 'normal', 'height': 'auto'},
            row_selectable='single',
            selected_rows=[]
        )
    ], style={'textAlign': 'center', 'width': '100%'})


def display_player_info(selected_rows, mode, table_data):
    if not selected_rows:
        return html.Div(), html.Div()

    player_index = selected_rows[0]
    df = pd.DataFrame(table_data)
    if player_index >= len(df):
        return html.Div(), html.Div()

    player_data = df.iloc[player_index]

    if mode != 'general':
        general_df = pd.read_excel('df_general_stats.xlsx')
        match = general_df[general_df['player_id'] == player_data['Matricule']]
        if not match.empty:
            player_data['Équipe'] = match['team'].values[0]
            player_data['Position'] = match['position_played'].values[0]

    player_info = html.Div([
        html.H3("Fiche Joueur"),
        html.P(f"Nom: {player_data.get('Joueur', 'N/A')}"),
        html.P(f"Équipe: {player_data.get('Équipe', 'N/A')}"),
        html.P(f"Poste: {player_data.get('Position', 'N/A')}")
    ])

    if mode == 'attack':
        histograms = create_offensive_histograms(player_data['Matricule'])
    elif mode == 'defense':
        histograms = create_defensive_histograms(player_data['Matricule'])
    elif mode == 'goalkeeper':
        histograms = create_goalkeeper_histograms(player_data['Matricule'])
    else:
        histograms = create_general_histograms(player_data['Matricule'])

    histogram_layout = html.Div([
        html.Div(dcc.Graph(figure=fig), style={'width': '50%', 'display': 'inline-block'})
        for fig in histograms
    ], style={'width': '100%', 'display': 'flex', 'flex-wrap': 'wrap'})

    return player_info, histogram_layout