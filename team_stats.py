import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output, callback

# ----------------------------------------------------------------
# 1. Data Loading and Processing
# ----------------------------------------------------------------

file_path = "data/L1QC.xlsx"
df_matchs = pd.read_excel(file_path, sheet_name="matchs")
df_teams = pd.read_excel(file_path, sheet_name="teams")

# Merge team names into df_matchs
df_matchs = df_matchs.merge(
    df_teams[['id', 'name']],
    left_on='team_id',
    right_on='id',
    how='left'
)

# Calculate possession
df_matchs['possession'] = (
    df_matchs['passes_bwd_successful'] + df_matchs['passes_fwd_successful'] +
    df_matchs['passes_left_successful'] + df_matchs['passes_right_successful']
) / (
    df_matchs['passes_right'] + df_matchs['passes_fwd'] +
    df_matchs['passes_bwd'] + df_matchs['passes_left']
)

# Convert 'goals_for' from string "x;x;x" to an integer count
def count_goals(goals_str):
    if isinstance(goals_str, str):
        return len(goals_str.split(";"))
    return 0
df_matchs['goals_for'] = df_matchs['goals_for'].apply(count_goals)

# Count cards
def count_cards(card_str):
    if isinstance(card_str, str):
        return len(card_str.split(";"))
    return 0
df_matchs['yellow_cards_for'] = df_matchs['yellow_cards_for'].apply(count_cards)
df_matchs['red_cards_for'] = df_matchs['red_cards_for'].apply(count_cards)
df_matchs['total_cards'] = df_matchs['yellow_cards_for'] + df_matchs['red_cards_for']

# Convert numeric columns
numeric_columns = [
    'shots', 'goals_for', 'possession', 'fouls_committed',
    'yellow_cards_for', 'red_cards_for', 'tackles_committed',
    'goals_against', 'total_cards', 'passes_fwd', 'passes_bwd',
    'aerial_challenges', 'aerial_challenges_successful'
]
for col in numeric_columns:
    df_matchs[col] = pd.to_numeric(df_matchs[col], errors='coerce').fillna(0)

# Aggregate stats by team
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

df_team_stats['team_id'] = df_team_stats['team_id'].astype(int)

# Prepare dropdown options
team_options = [{'label': "Aucune sélection", 'value': None}] + [
    {'label': name, 'value': int(team_id)}
    for team_id, name in zip(df_team_stats['team_id'], df_team_stats['name'])
]

stat_types = [
    {'label': "Offensif", 'value': "offensif"},
    {'label': "Défensif", 'value': "defensif"},
    {'label': "Possession", 'value': "possession"}
]

# ----------------------------------------------------------------
# 2. Layout
# ----------------------------------------------------------------

layout = html.Div([
    html.Div([
        html.H3("Statistiques des Équipes",
                style={'display': 'inline-block', 'margin-right': '20px'}),
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
            value=["show"],
            style={'margin-left': '20px', 'margin-bottom': '10px'}
        )
    ], style={'display': 'flex', 'alignItems': 'center'}),

    # Two graphs side by side
    html.Div([
        dcc.Graph(id="scatter-graph-1", style={'width': '48%', 'display': 'inline-block'}),
        dcc.Graph(id="scatter-graph-2", style={'width': '48%', 'display': 'inline-block'})
    ]),

    # Two tables side by side
    html.Div([
        html.Div(id="table-1",
                 style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        html.Div(id="table-2",
                 style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'marginTop': '20px'})
])

# ----------------------------------------------------------------
# 3. Helper Functions
# ----------------------------------------------------------------

def build_table(df, top_n=3):
    """
    Sort df by 'ratio' desc, take top_n, return an html.Table.
    """
    df_top = df.sort_values("ratio", ascending=False).head(top_n)
    return html.Table(
        [
            html.Thead(html.Tr([html.Th("Équipe"), html.Th("Ratio")])),
            html.Tbody([
                html.Tr([
                    html.Td(row["name"]),
                    html.Td(f"{row['ratio']:.2f}")
                ])
                for _, row in df_top.iterrows()
            ])
        ],
        style={
            "width": "100%",
            "textAlign": "center",
            "border": "1px solid black",
            "marginTop": "10px"
        }
    )

# ----------------------------------------------------------------
# 4. Callback
# ----------------------------------------------------------------

@callback(
    [
        Output("scatter-graph-1", "figure"),
        Output("scatter-graph-2", "figure"),
        Output("table-1", "children"),
        Output("table-2", "children")
    ],
    [
        Input("team-dropdown", "value"),
        Input("stat-type-dropdown", "value"),
        Input("toggle-names", "value")
    ]
)
def update_graphs(selected_team, stat_type, show_names):
    show_text = "show" in show_names

    # Always work on a local copy to avoid modifying the global DataFrame
    df = df_team_stats.copy()

    # Convert selected_team to int if possible
    if selected_team is not None:
        try:
            selected_team = int(selected_team)
        except ValueError:
            selected_team = None

    # Explicitly set the highlight based on whether selected_team is None or not
    if selected_team is None:
        df["highlight"] = False
    else:
        df["highlight"] = df["team_id"] == selected_team

    # Explicitly compute marker colors from the highlight column
    colors = ["red" if flag else "blue" for flag in df["highlight"]]

    if stat_type == "offensif":
        # Left graph: Shots vs Goals
        x_left, y_left = "shots", "goals_for"
        # Right graph: Possession vs Goals
        x_right, y_right = "possession", "goals_for"

        fig_left = px.scatter(
            df,
            x=x_left, y=y_left,
            text=df["name"] if show_text else None,
            title="Relation entre tirs et buts marqués",
            labels={x_left: "Nombre total de tirs", y_left: "Nombre de buts marqués"},
            hover_data=["name", x_left, y_left]
        )
        fig_left.update_traces(marker=dict(color=colors))

        fig_right = px.scatter(
            df,
            x=x_right, y=y_right,
            text=df["name"] if show_text else None,
            title="Relation entre possession et buts marqués",
            labels={x_right: "Pourcentage de possession", y_right: "Nombre de buts marqués"},
            hover_data=["name", x_right, y_right]
        )
        fig_right.update_traces(marker=dict(color=colors))

        df_temp_left = df.copy()
        df_temp_left["ratio"] = df_temp_left.apply(
            lambda row: row[y_left] / row[x_left] if row[x_left] != 0 else 0, axis=1
        )
        df_temp_right = df.copy()
        df_temp_right["ratio"] = df_temp_right.apply(
            lambda row: row[y_right] / row[x_right] if row[x_right] != 0 else 0, axis=1
        )

    elif stat_type == "defensif":
        # Left graph: Fouls vs Total Cards
        x_left, y_left = "fouls_committed", "total_cards"
        # Right graph: Tackles vs Goals Against
        x_right, y_right = "tackles_committed", "goals_against"

        fig_left = px.scatter(
            df,
            x=x_left, y=y_left,
            text=df["name"] if show_text else None,
            title="Fautes commises vs Nombre total de cartons",
            labels={x_left: "Nombre de fautes", y_left: "Total des cartons"},
            hover_data=["name", x_left, "yellow_cards_for", "red_cards_for"]
        )
        fig_left.update_traces(marker=dict(color=colors))

        fig_right = px.scatter(
            df,
            x=x_right, y=y_right,
            text=df["name"] if show_text else None,
            title="Tacles réalisés vs Buts concédés",
            labels={x_right: "Total des tacles", y_right: "Buts concédés"},
            hover_data=["name", x_right, y_right]
        )
        fig_right.update_traces(marker=dict(color=colors))

        df_temp_left = df.copy()
        df_temp_left["ratio"] = df_temp_left.apply(
            lambda row: row[y_left] / row[x_left] if row[x_left] != 0 else 0, axis=1
        )
        df_temp_right = df.copy()
        df_temp_right["ratio"] = df_temp_right.apply(
            lambda row: row[x_right] / (row[y_right] + 1), axis=1
        )

    else:  # "possession" or any other category
        # Left graph: Passes Forward vs Passes Backward
        x_left, y_left = "passes_fwd", "passes_bwd"
        # Right graph: Aerial Challenges vs Aerial Challenges Successful
        x_right, y_right = "aerial_challenges", "aerial_challenges_successful"

        fig_left = px.scatter(
            df,
            x=x_left, y=y_left,
            text=df["name"] if show_text else None,
            title="Passes en avant vs Passes en retrait",
            labels={x_left: "Passes en avant", y_left: "Passes en retrait"},
            hover_data=["name", x_left, y_left]
        )
        fig_left.update_traces(marker=dict(color=colors))

        fig_right = px.scatter(
            df,
            x=x_right, y=y_right,
            text=df["name"] if show_text else None,
            title="Duels aériens remportés vs Duels aériens totaux",
            labels={x_right: "Duels aériens", y_right: "Duels gagnés"},
            hover_data=["name", x_right, y_right]
        )
        fig_right.update_traces(marker=dict(color=colors))

        df_temp_left = df.copy()
        df_temp_left["ratio"] = df_temp_left.apply(
            lambda row: row[x_left] / (row[y_left] + 1), axis=1
        )
        df_temp_right = df.copy()
        df_temp_right["ratio"] = df_temp_right.apply(
            lambda row: row[y_right] / (row[x_right] + 1), axis=1
        )

    table_left = build_table(df_temp_left)
    table_right = build_table(df_temp_right)

    return fig_left, fig_right, table_left, table_right
