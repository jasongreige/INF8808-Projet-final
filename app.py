import dash
from dash import dcc, html
from team_stats import layout as team_stats_layout
from dash import dash_table
from matchs_table import df_resultats, df_match_stats
from matchs_table import layout as matchs_table_layout
from display_match import generate_score_table, generate_match_details


app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # Important pour Flask

# Définition des onglets et de la mise en page
app.layout = html.Div([
    html.H1("Soccer Stats Québec", style={
        'textAlign': 'center',
        'fontFamily': 'Arial Black, sans-serif',
        'fontSize': '36px',
        'marginTop': '30px',
        'color': '#2C4F8E',
        'textShadow': '1px 1px 2px rgba(0,0,0,0.1)'
    }),

    html.Div([
        dcc.Tabs(
            id="tabs",
            value="team_stats",
            children=[
                dcc.Tab(label="📊 Matchs", value="matchs", className="custom-tab", selected_className="custom-tab--selected"),
                dcc.Tab(label="📈 Statistiques des Équipes", value="team_stats", className="custom-tab", selected_className="custom-tab--selected"),
                dcc.Tab(label="🧍‍♂️ Statistiques des Joueurs", value="player_stats", className="custom-tab", selected_className="custom-tab--selected")
            ],
            parent_className="custom-tabs",
            className="custom-tabs-container"
        ),
        html.Div(id="tabs-content", style={
            'padding': '20px',
            'backgroundColor': '#ffffff',
            'borderRadius': '10px',
            'boxShadow': '0 2px 6px rgba(0,0,0,0.1)',
            'marginTop': '10px'
        })
    ], style={
        'width': '100%',
        'margin': 'auto',
        'marginBottom': '40px'
    })
])

# Callback pour afficher le bon contenu selon l'onglet sélectionné
@app.callback(
    dash.Output("tabs-content", "children"),
    [dash.Input("tabs", "value")]
)
def update_tab(tab_name):
    if tab_name == "team_stats":
        return team_stats_layout  # On affiche l'onglet Team Stats
    elif tab_name == "player_stats":
        return html.Div([
            html.H3("Statistiques des Joueurs"),
            html.P("Contenu à ajouter ici...")
        ])
    elif tab_name == "matchs":
        return matchs_table_layout
    return html.Div("Sélectionnez un onglet.")

if __name__ == "__main__":
    app.run_server(debug=True)

################### Callback match

@app.callback(
    dash.Output("filtered-table", "children"),
    [dash.Input("equipe-filter", "value")]
)
def update_table(equipe):
    return generate_score_table(df_resultats, equipe)
    
    
@app.callback(
    dash.Output("match-details", "children"),
    [dash.Input("score-table", "selected_rows"),
     dash.Input("equipe-filter", "value")]
)
def update_details(selected_rows, equipe):
    return generate_match_details(df_resultats, df_match_stats, selected_rows, equipe)