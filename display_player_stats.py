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

#======================================================================
#                      Barres %                                       #
#======================================================================



def create_bar_column(df, column, color="#2C4F8E"):  #afficher avec barre bleue
    max_val = df[column].max()
    
    def render_bar(value):
        percent = (value / max_val) * 100 if max_val != 0 else 0
        return f'<div style="width: 100%; background-color: #e0e0e0; border-radius: 3px;"><div style="width: {percent:.1f}%; background-color: {color}; padding: 2px 4px; border-radius: 3px; color: white; font-size: 11px; font-weight: bold; text-align: right;">{value}</div></div>'

    
    df[column] = df[column].fillna(0).astype(int).apply(render_bar)
    return df

def generate_percentage_gradient_styles(df, percent_columns): #couleur ds cases en %
    styles = []
    for col in percent_columns:
        if col not in df.columns:
            continue
        values = pd.to_numeric(df[col].str.replace('%', ''), errors='coerce')
        min_val, max_val = values.min(), values.max()

        for i, val in enumerate(values):
            if pd.isna(val):
                continue
            normalized = (val - min_val) / (max_val - min_val) if max_val > min_val else 0
            blue_intensity = int(255 - normalized * 120)  # 255 (blanc) -> 135 (bleu foncé)
            bg_color = f"rgb({blue_intensity}, {blue_intensity}, 255)"
            styles.append({
                'if': {
                    'filter_query': f'{{{col}}} = "{int(round(val))}%"',
                    'column_id': col
                },
                'backgroundColor': bg_color,
                'color': 'black'
            })
    return styles


def update_player_table(mode, league, search_value, stored_player_id):
    df_raw = pd.read_excel(f'{MODES[mode]["dataframe"]}.xlsx')
    df = df_raw.copy()

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
        'goals_and_assists': 'Buts+Passes décisives',
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
        'gk_clearances_(%)': 'Réussite dégagements gardien (%)',
        'precision_passes_(%)': 'Réussite passes (%)'
    })

    # Colonnes à masquer
    colonnes_visibles = [col for col in df.columns if col not in ["Saison", "Matricule"]]

    df_display = df.copy()
    
    if search_value:
        df = df[df['Joueur'].str.contains(search_value, case=False, na=False)]

    # Liste des colonnes %
    percent_cols = [
        'Réussite tirs (%)', 'Réussite dribbles (%)', 'Réussite duels (%)',
        'Réussite duels aériens (%)', 'Réussite dégagements (%)',
        'Réussite tacles (%)', 'Réussite passes (%)', 'Réussite dégagements gardien (%)'
    ]

    for col in percent_cols:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: f"{int(round(x))}%" if pd.notnull(x) else "–")

    # Barres uniquement sur la version affichée
    for col in ['Tirs', 'Passes', 'Buts+Passes décisives', 'Interceptions']:
        if col in df_display.columns:
            df_display = create_bar_column(df_display, col)

    style_conditional = generate_percentage_gradient_styles(df_display, percent_cols) # on génére le style pour les cases en %


    # === DataTable
    return html.Div([
        html.H3('Tableau des statistiques intéractif', style={'font-size': '20px'}),
        html.Div([
        html.P("Plus la couleur est foncée, meilleure est la statistique en pourcentage.",
               style={
                   'fontSize': '13px',
                   'fontStyle': 'italic',
                   'marginBottom': '10px',
                   'color': '#333'
               })
    ]),
        dash_table.DataTable(
            id='table',
            fixed_rows={'headers': True},
            columns=[{'name': col, 'id': col, 'presentation': 'markdown'} for col in colonnes_visibles],
            data=df_display.to_dict('records'),
            markdown_options={"html": True},
            style_table={
                'maxHeight': '650px',
                'width': '100%',
                'borderRadius': '8px',
                'boxShadow': '0 2px 6px rgba(0,0,0,0.1)',
                'border': '1px solid #ccc'
            },
            style_cell={
                'textAlign': 'center',
                'whiteSpace': 'normal',
                'height': 'auto',
                'fontFamily': 'Arial, sans-serif',
                'fontSize': '12px',
                'padding': '8px',
                'minWidth': '120px',
                'width': '90px',
                'maxWidth': '120px',
                'borderRight': '1px solid #ccc',
                'borderLeft': '1px solid #ccc'
            },
            style_data={
                'backgroundColor': 'white',
                'borderBottom': '1px solid #ddd',
            },
            style_header={
                'backgroundColor': '#eef4fb', 
                'fontWeight': 'bold',
                'textAlign': 'center',
                'fontSize': '12px',
                'borderBottom': '2px solid #bbb',
                'borderTop': '2px solid #bbb'
            },
            style_data_conditional=style_conditional,
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