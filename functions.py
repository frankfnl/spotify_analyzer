import dash
from dash import Dash, html, dcc, Output, Input
import plotly.express as px
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import dash_bootstrap_components as dbc

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
                    dbc.Col([image], width=2),
                    dbc.Col(
                        [
                            dbc.Row([dbc.Col([title])]),
                            dbc.Row([dbc.Col([subtitle])]),
                        ],
                        width=10)
                ]
            ),
        ],
        className='track-card recent-track-card',
    )

    return container_item

def top_tracks(range, sp_auth):
    scope = 'user-top-read'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    dict_ranges = {
        'Last 4 Weeks' :    'short_term',
        'Last 6 Months':    'medium_term',
        'All Time':         'long_term'
    }

    results = sp.current_user_top_tracks(time_range=dict_ranges[range], limit=12)
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

def recent_tracks():
    scope='user-read-recently-played'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    results = sp.current_user_recently_played(limit=7)
    items = [recent_track_div(item) for item in results['items']]
    title = html.H4(f"Recently played", className="section-header")
    children = [dbc.Row([dbc.Col([items[i]])]) for i in (range(len(items)))]
    children.insert(0, dbc.Row([dbc.Col([title])]))
    container = html.Div(
        children,
        className='top-tracks-card-container',
    )
    return container


def get_callbacks(app):
    @app.callback(
        Output('top-tracks', 'children'),
        Input('tracks-range-radio', 'value'),
    )
    def top_tracks_callback(value):
        return top_tracks(value)