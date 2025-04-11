from dash import html, dash_table

from dash import dash_table
from dash import dcc

from matchs_table import extract_events_from_match_row, df_matchs_masculins

from collections import defaultdict

# =============== Table des scores ================

def generate_score_table(df_resultats, equipe):
    if equipe is None:
        filtered_df = df_resultats
    else:
        filtered_df = df_resultats[
            (df_resultats["home_team"] == equipe) | (df_resultats["away_team"] == equipe)
        ]

    # Mise en gras du gagnant
    def highlight_winner(row):
        try:
            h, a = map(int, row["score"].split("-"))
            home_win = h > a
            away_win = a > h
        except:
            return row["home_team"], row["score"], row["away_team"]
        
        home = f"**{row['home_team']}**" if home_win else row["home_team"]
        away = f"**{row['away_team']}**" if away_win else row["away_team"]
        return home, row["score"], away

    table_data = []
    for _, row in filtered_df.iterrows():
        home, score, away = highlight_winner(row)
        table_data.append({
            "home_team": home,
            "score": score,
            "away_team": away
        })

    return dash_table.DataTable(
        id="score-table",
        data=table_data,
        columns=[
            {"name": "Home team", "id": "home_team", "presentation": "markdown"},
            {"name": "Final score", "id": "score"},
            {"name": "Away team", "id": "away_team", "presentation": "markdown"},
        ],
        page_size=15,
        row_selectable="single",  
        selected_rows=[],        
        style_table={'overflowX': 'auto'},
        style_cell={
            'fontFamily': 'Arial, sans-serif',
            'fontSize': '15px',         
            'padding': '4px 8px',       
            'whiteSpace': 'normal',
            'height': 'auto'
        },
        style_header={
            'backgroundColor': '#eef4fb',
            'fontWeight': 'bold',
            'textAlign': 'center'
        },
        style_data_conditional=[
            {
                'if': {'column_id': 'score'},
                'backgroundColor': '#2C4F8E', 
                'color': 'white',              
                'textAlign': 'center',
                'fontWeight': 'bold'
            },
            {
                'if': {'column_id': 'home_team'},
                'textAlign': 'center' 
            },
            {
                'if': {'column_id': 'away_team'},
                'textAlign': 'center'
            }
        ],
        style_as_list_view=True
    )

# =======================================

            # En tête #
            
# =======================================

def generate_match_header(home_team, away_team, score, match_date):
    return html.Div([
        html.Div([
            # Ligne noms des équipes et score
            html.Div([
                html.Div(home_team, style={
                    'flex': '1',
                    'textAlign': 'right',
                    'fontWeight': 'bold',
                    'fontSize': '20px',
                    'fontFamily': 'Arial, sans-serif',
                    'color': '#333'
                }),
                html.Div(score, style={
                    'flex': '1',
                    'textAlign': 'center',
                    'fontWeight': 'bold',
                    'fontSize': '28px',
                    'fontFamily': 'Arial Black, sans-serif',
                    'color': '#4b0082'
                }),
                html.Div(away_team, style={
                    'flex': '1',
                    'textAlign': 'left',
                    'fontWeight': 'bold',
                    'fontSize': '20px',
                    'fontFamily': 'Arial, sans-serif',
                    'color': '#333'
                }),
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center',
                'width': '100%',
                'marginBottom': '5px'
            }),

            # Date du match en dessous
            html.Div(match_date, style={
                'textAlign': 'center',
                'fontSize': '14px',
                'color': '#666',
                'fontFamily': 'Arial, sans-serif'
            })
        ])
    ], style={
        'backgroundColor': 'white',
        'borderRadius': '10px',
        'padding': '12px 20px',
        'marginBottom': '15px',
        'boxShadow': '0 2px 6px rgba(0,0,0,0.1)',
        'width': '95%'
    })

    
# ========================================
             # FRISE # 
# ========================================

def convert_minute_to_percent(minute):
    """
    Convertit une minute (0 à 120) en pourcentage horizontal sur la frise (0 à 100%).
    """
    m = int(str(minute).replace("+", "").strip())
    max_minute = 90  # Pour prendre en compte les arrêts de jeu
    return min(100, max(0, m / max_minute * 100))

def add_tooltips_to_events(events):
    """
    Ajoute un champ 'tooltip' à chaque événement dans la liste.
    """
    for e in events:
        if e["type"] == "goal" and "player" in e and e["player"]:
            e["tooltip"] = f"Buteur : {e['player']}"
        elif e["type"] == "yellow_card" and "player" in e and e["player"]:
            e["tooltip"] = f"Averti : {e['player']}"
        elif e["type"] == "red_card" and "player" in e and e["player"]:
            e["tooltip"] = f"Expulsé : {e['player']}"
        elif e["type"] == "substitution" and "player_in" in e and "player_out" in e:
            e["tooltip"] = f"{e['player_out']} → {e['player_in']}"
        else:
            e["tooltip"] = e.get("type").capitalize()
    return events

def generate_vertical_timeline_bar(events, home_team_name, away_team_name):
    icons = {
        "goal": "⚽️",
        "yellow_card": "🟨",
        "red_card": "🟥",
        "substitution": "🔄"
    }

    elements = []

    # Ligne centrale
    elements.append(html.Div(style={
        'position': 'absolute',
        'top': '50%',
        'left': '1%',
        'width': '97%',
        'height': '3px',
        'backgroundColor': '#4b0082',
        'transform': 'translateY(-50%)'
    }))

    # Labels KO / FT
    elements += [
        html.Div("KO", style={
            'position': 'absolute',
            'left': '2%',
            'top': '62%',
            'transform': 'translate(-50%, -50%)',
            'fontWeight': 'bold',
            'fontFamily': 'Arial'
        }),
        html.Div("FT", style={
            'position': 'absolute',
            'left': '98%',
            'top': '62%',
            'transform': 'translate(-50%, -50%)',
            'fontWeight': 'bold',
            'fontFamily': 'Arial'
        }),
        html.Div(home_team_name, style={
            'position': 'absolute',
            'top': '5%',
            'left': '2%',
            'fontWeight': 'bold',
            'fontSize': '14px',
            'fontFamily': 'Arial',
            'color': '#333'
        }),
        html.Div(away_team_name, style={
            'position': 'absolute',
            'bottom': '5%',
            'left': '2%',
            'fontWeight': 'bold',
            'fontSize': '14px',
            'fontFamily': 'Arial',
            'color': '#333'
        })
    ]

    # Group by minute
    grouped = defaultdict(list)
    for e in events:
        grouped[int(e["minute"])].append(e)

    sorted_minutes = sorted(grouped.keys())
    used_positions = []
    used_minutes = []
    min_spacing = 2.5

    def convert_minute_to_percent(minute):
        try:
            minute = int(minute)
        except:
            return 0
        return max(0, min(95, (minute / 90) * 100 * 0.95))

    def adjust_position(minute, raw_pos):
        for i, prev_pos in enumerate(used_positions):
            prev_minute = used_minutes[i]
            time_diff = abs(minute - prev_minute)
            space_needed = max(min_spacing, 6 - time_diff)
            if abs(raw_pos - prev_pos) < space_needed:
                raw_pos = max(used_positions) + space_needed
        used_positions.append(raw_pos)
        used_minutes.append(minute)
        return raw_pos

    for minute in sorted_minutes:
        group = grouped[minute]
        raw_percent = convert_minute_to_percent(minute)
        percent = adjust_position(minute, raw_percent)
        home_idx = 0
        away_idx = 0

        for e in group:
            icon = icons[e["type"]]
            team = e["team"]
            tooltip = e.get("tooltip", "")
            if team == "home":
                offset = 20 + home_idx * 20
                elements += [
                    html.Div(style={
                        'position': 'absolute',
                        'left': f'{percent}%',
                        'bottom': '50%',
                        'height': '20px',
                        'width': '2px',
                        'backgroundColor': '#555',
                    }),
                    html.Div([
                        html.Div(icon, className="tooltip-icon"),
                        html.Div(tooltip, className="tooltip-text")
                    ], className="tooltip-container", style={
                        'position': 'absolute',
                        'left': f'{percent}%',
                        'bottom': f'calc(50% + {offset}px)',
                        'transform': 'translateX(-50%)'
                    })
                ]
                home_idx += 1
            else:
                offset = 20 + away_idx * 20
                elements += [
                    html.Div(style={
                        'position': 'absolute',
                        'left': f'{percent}%',
                        'top': '50%',
                        'height': '20px',
                        'width': '2px',
                        'backgroundColor': '#555',
                    }),
                    html.Div([
                        html.Div(icon, className="tooltip-icon"),
                        html.Div(tooltip, className="tooltip-text")
                    ], className="tooltip-container", style={
                        'position': 'absolute',
                        'left': f'{percent}%',
                        'top': f'calc(50% + {offset}px)',
                        'transform': 'translateX(-50%)'
                    })
                ]
                away_idx += 1

        # Minute unique
        elements.append(html.Div(f"{minute}'", style={
            'position': 'absolute',
            'left': f'{percent}%',
            'top': '50%',
            'transform': 'translate(-50%, -50%)',
            'fontSize': '12px',
            'color': '#4b0082',
            'fontFamily': 'Arial',
            'fontWeight': 'bold',
            'backgroundColor': '#f8f8f8',
            'padding': '2px 4px',
            'borderRadius': '3px'
        }))

    return html.Div([
        html.Div(elements, style={
            'position': 'relative',
            'height': '220px',
            'marginTop': '30px',
            'marginBottom': '30px',
            'width': '100%',
            'backgroundColor': '#f8f8f8',
            'borderRadius': '8px',
            'boxShadow': '0 2px 6px rgba(0,0,0,0.1)',
        })
    ])
    
    


    # =========================================
    #               Table de stats
    #==========================================

def generate_match_details(df_resultats, df_match_stats, selected_rows, equipe):
    if not selected_rows:
        return html.P("Cliquez sur un match pour voir ses statistiques.")

    if equipe is None:
        filtered_df = df_resultats
    else:
        filtered_df = df_resultats[
            (df_resultats["home_team"] == equipe) | (df_resultats["away_team"] == equipe)
        ]

    selected_index = selected_rows[0]
    selected_row = filtered_df.iloc[selected_index]
    match_id = selected_row["match_id"]
    home = selected_row["home_team"]
    away = selected_row["away_team"]

    stats = df_match_stats[df_match_stats["match_id"] == match_id].squeeze()
    # retrouver la ligne complète dans le dataframe d'origine
    
    full_match_row = df_matchs_masculins[df_matchs_masculins["id"] == match_id].squeeze()
    events = extract_events_from_match_row(full_match_row)
    timeline_bar = generate_vertical_timeline_bar(events, selected_row["home_team"],selected_row["away_team"])

    
    cell_style = {
        'textAlign': 'center',
        'padding': '10px',
        'fontFamily': 'Arial, sans-serif',
        'fontSize': '16px',
        'width': '33%'
    }

    def bold(val1, val2):
        return {'fontWeight': 'bold' if val1 > val2 else 'normal'}

    def stat_row(val_home, label, val_away, zebra=False):
        row_style = {'backgroundColor': '#f9f9f9'} if zebra else {}
        try:
            val_home_f = float(val_home)
            val_away_f = float(val_away)
        except:
            val_home_f, val_away_f = 0, 0

        return html.Tr([
            html.Td(val_home, style={**cell_style, **bold(val_home_f, val_away_f)}),
            html.Td(label, style=cell_style),
            html.Td(val_away, style={**cell_style, **bold(val_away_f, val_home_f)})
        ], style=row_style)

    rows = [
        stat_row(stats["possession_home"], "Possession %", stats["possession_away"]),
        stat_row(stats["shots_on_home"], "Shots on target", stats["shots_on_away"], zebra=True),
        stat_row(stats["shots_home"], "Shots", stats["shots_away"]),
        stat_row(stats["total_passes_home"], "Passes", stats["total_passes_away"], zebra=True),
        stat_row(stats["offsides_home"], "Offsides", stats["offsides_away"]),
        stat_row(stats["freekicks_home"], "Free kicks", stats["freekicks_away"], zebra=True),
        stat_row(stats["corners_home"], "Corners", stats["corners_away"]),
        stat_row(stats["fouls_committed_home"], "Fouls committed", stats["fouls_committed_away"], zebra=True)
    ]
    header = generate_match_header(selected_row["home_team"],selected_row["away_team"],selected_row["score"],selected_row["date"])  # adapte ici selon ta colonne réelle)
    
    
    
    return html.Div([
        html.H4("Statistiques du match", style={
            'textAlign': 'center',
            'fontFamily': 'Arial, sans-serif',
            'fontSize': '24px',
            'marginBottom': '20px'
        }),
        header,
        html.Div(timeline_bar, style={
        'border': '2px black',
        'padding': '2px',
        'marginBottom': '20px',
        'borderRadius': '6px'
    }),

        html.Table([
            html.Thead(
                html.Tr([
                    html.Th(home, style={**cell_style, 'fontWeight': 'bold'}),
                    html.Th("Statistique", style={**cell_style}),
                    html.Th(away, style={**cell_style, 'fontWeight': 'bold'})
                ])
            ),
            html.Tbody(rows)
        ], style={
            'width': '100%',
            'borderCollapse': 'collapse',
            'marginTop': '15px',
            'boxShadow': '2px 2px 8px rgba(0,0,0,0.1)',
            'borderRadius': '8px',
            'overflow': 'hidden',
            'fontFamily': 'Arial, sans-serif',
        })
    ])