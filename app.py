import dash
from dash import Dash, html, dcc, Output, Input
from dotenv import load_dotenv
import dash_bootstrap_components as dbc
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import plotly.express as px
import pandas as pd

#Load environment variables
load_dotenv()

#Spotipy Authentication
top_scope = 'user-top-read'
sp_top = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=top_scope))
recent_scope = 'user-read-recently-played'
sp_recent = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=recent_scope))

def top_track_div(item):
    image = dbc.CardImg(src=item['album']['images'][0]['url'], top=True)
    track_name = item['name']
    artist_name = item['artists'][0]['name']
    track_id = f'Spotify ID: {item["id"]}'
    title = html.P(track_name, className='text-top-track')
    subtitle = html.P(artist_name, className='subtitle-top-track')

    container_item = html.Div(
        [
            dbc.Row([dbc.Col([image])]),
            dbc.Row([dbc.Col([title])]),
            dbc.Row([dbc.Col([subtitle])]),
        ],
        className='track-card',
    )
    
    return container_item

def recent_track_div(item):
    image = dbc.CardImg(src=item['track']['album']['images'][0]['url'], top=True)
    track_name = item['track']['name']
    artist_name = item['track']['artists'][0]['name']
    title = html.P(track_name, className='text-top-track text-recent-track')
    subtitle = html.P(artist_name, className='subtitle-top-track')

    container_item = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col([image], className='image-recent-track', width=3),
                    dbc.Col(
                        [
                            dbc.Row([dbc.Col([title])]),
                            dbc.Row([dbc.Col([subtitle])]),
                        ],
                        width=8)
                ]
            ),
        ],
        className='track-card recent-track-card',
    )

    return container_item

def top_tracks(range, sp_auth):
    dict_ranges = {
        'Last 4 Weeks' :    'short_term',
        'Last 6 Months':    'medium_term',
        'All Time':         'long_term'
    }

    results = sp_auth.current_user_top_tracks(time_range=dict_ranges[range], limit=12)
    title = html.H4(f"Top Tracks: {range}", className="section-header")

    container = html.Div(
        [
            dbc.Row([dbc.Col([title])]),
            dbc.Row([]),
            dbc.Row([]),
            dbc.Row([]),
        ],
        className='top-tracks-card-container',
    )

    items = [top_track_div(item) for item in results['items']]
    def row(items):
        return dbc.Row([dbc.Col([i]) for i in items])
    row1 = row(items[:4])
    row2 = row(items[4:8])
    row3 = row(items[8:12])
    container.children[1].children = row1
    container.children[2].children = row2
    container.children[3].children = row3
    return container

def recent_tracks(sp_auth):
    results = sp_auth.current_user_recently_played(limit=7)
    items = [recent_track_div(item) for item in results['items']]
    title = html.H4(f"Recently played", className="section-header")
    children = [dbc.Row([dbc.Col([items[i]])]) for i in (range(len(items)))]
    children.insert(0, dbc.Row([dbc.Col([title])]))
    container = html.Div(
        children,
        className='top-tracks-card-container',
    )
    return container

#App Layout Components
header = html.P("Spotify Dashboard", className="app-header")
tracks_range_radio = html.Div(
    [
        dcc.RadioItems(['Last 4 Weeks', 'Last 6 Months','All Time'],
        'Last 4 Weeks',
        id='tracks-range-radio',
        className='horizontal-radio')
    ],
    className='radio-container',
)

card_top_tracks = html.Div([], id='top-tracks')
card_recent_tracks = html.Div([recent_tracks(sp_recent)], id='recent-tracks')
card_patterns = []
card_genres = []
card_playlists = []
card_history = []
card_mood = []

#Initialize App
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#Callbacks
@app.callback(
    Output('top-tracks', 'children'),
    Input('tracks-range-radio', 'value'),
)
def top_tracks_callback(value):
    return top_tracks(value, sp_top)

#App Layout
app.layout = dbc.Container(
    [
        dbc.Row(dbc.Col([header])),
        dbc.Row(
            [
                dbc.Col([card_recent_tracks], width=2, className='column-container'),
                dbc.Col([card_top_tracks, tracks_range_radio], width=4, className='column-container'),
                dbc.Col([card_genres], width=4)
            ]
        ),
        dbc.Row(
            [
                dbc.Col([card_playlists], width=4),
                dbc.Col([card_history], width=4),
                dbc.Col([card_mood], width=4)
            ]
        ),
    ],
    className="dbc",
    fluid=True,
    id="main-container",
)

if __name__ == '__main__':
    app.run(debug=True, threaded=True)