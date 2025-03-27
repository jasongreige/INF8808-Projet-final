import dash
from dash import dcc, html
from team_stats import layout as team_stats_layout

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
        return html.Div([
            html.H3("Matchs"),
            html.P("Calendrier des matchs à afficher ici...")
        ])
    return html.Div("Sélectionnez un onglet.")

if __name__ == "__main__":
    app.run_server(debug=True)
