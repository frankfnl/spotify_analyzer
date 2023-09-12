import dash
from dash import Dash, html, dcc, Output, Input, State, callback, ClientsideFunction
from dash.exceptions import PreventUpdate
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
from flask import Flask
from flask_caching import Cache
import pathlib
import json
import inspect, os.path
from pathlib import Path
import pickle

#Initialize App
dbc_css = 'https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css'
app = Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    external_scripts = [
        {
            'src': 'https://kit.fontawesome.com/4ed21bb725.js',
            'crossorigin': 'anonymous',
        },
    ],
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}])
server = app.server
app.title = 'Spotify Dashboard'

#Load environment variables
load_dotenv()

#Spotify data
filename = inspect.getframeinfo(inspect.currentframe()).filename
current_directory = os.path.dirname(os.path.abspath(filename))
current_directory = current_directory.replace('\\','/')
spotify_data_path = Path(current_directory + '/streaming_history.csv')
spotify_df = pd.read_csv(spotify_data_path)


def top_track_div(item):
    image = dbc.CardImg(src=item['album']['images'][0]['url'], top=True, className='image-top-track')
    track_name = item['name']
    artist_name = item['artists'][0]['name']
    track_id = f'Spotify ID: {item["id"]}'
    title = html.P(track_name, className='text-top-track')
    title = html.A(title, href=item['external_urls']['spotify'], target='_blank')
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
    title = html.A(title, href=item['track']['external_urls']['spotify'], target='_blank')
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

def top_tracks(range):
    # top_scope = 'user-top-read'
    # sp_auth = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=top_scope))
    dict_ranges = {
        'Last 4 Weeks' :    'short_term',
        'Last 6 Months':    'medium_term',
        'All Time':         'long_term'
    }

    # results = sp_auth.current_user_top_tracks(time_range=dict_ranges[range], limit=12)
    
    # # save dictionary to top_tracks.pkl file
    # with open(f'top_tracks_{dict_ranges[range]}.pkl', 'wb') as fp:
    #     pickle.dump(results, fp)
    #     print('dictionary saved successfully to file')

    # Read dictionary pkl file
    top_tracks_path = Path(current_directory + f'/top_tracks_{dict_ranges[range]}.pkl')
    with open(top_tracks_path, 'rb') as fp:
        results = pickle.load(fp)
        title = html.H4(f'Top Tracks: {range}', className='section-header')
        items = [top_track_div(item) for item in results['items']]

        container = html.Div(
            [
                dbc.Row([dbc.Col([title])]),
                dbc.Row([
                    dbc.Col(items[:3], width=6, lg=3),
                    dbc.Col(items[3:6], width=6, lg=3),
                    dbc.Col(items[6:9], width=6, lg=3),
                    dbc.Col(items[9:12], width=6, lg=3),
                ]),
            ],
            className='top-tracks-card-container',
        )

        # def row(items):
        #     return dbc.Row([dbc.Col([i]) for i in items])
        # row1 = row()
        # row2 = row(items[4:8])
        # row3 = row(items[8:12])
        # container.children[1].children = row1
        # container.children[2].children = row2
        # container.children[3].children = row3
        return container

def recent_tracks():
    # recent_scope = 'user-read-recently-played'
    # sp_auth = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=recent_scope))
    # results = sp_auth.current_user_recently_played(limit=7)
    # # save dictionary to top_tracks.pkl file
    # with open('recent_tracks.pkl', 'wb') as fp:
    #     pickle.dump(results, fp)
    #     print('dictionary saved successfully to file')

    # Read dictionary pkl file
    recent_tracks_path = Path(current_directory + '/recent_tracks.pkl')
    with open(recent_tracks_path, 'rb') as fp:
        results = pickle.load(fp)
        title = html.H4(f'Top Tracks: {range}', className='section-header')
        items = [recent_track_div(item) for item in results['items']]
        title = html.H4(f'Recently played', className='section-header')
        children = [dbc.Row([dbc.Col([items[i]])]) for i in (range(len(items)))]
        children.insert(0, dbc.Row([dbc.Col([title])]))
        container = html.Div(
            children,
            className='top-tracks-card-container',
        )
        return container

def user_stats():
    df = spotify_df.copy()
    total_time = df['msPlayed'].sum()
    total_time_minutes = round(total_time / 60000)
    total_time_hours = round(total_time / 3600000)
    total_time_days = round(total_time_hours / 24)
    total_tracks = df.shape[0]
    total_artists = df['artistName'].nunique()
    df['trackLength'] = df['msPlayed'] / 60000
    avg_track_length = round(df['trackLength'].mean(), 2)


    dict_stats = {
        'Minutes listened' : total_time_minutes,
        'Days listened' : total_time_days,
        'Tracks' : total_tracks,
        'Artists' : total_artists,
        'Average track length' : f'{avg_track_length} min'
    }

    stats = dbc.Container(
        [
            dbc.Stack(
                [
                    dbc.Row(
                        [
                            html.P(k, className='title-stats'),
                            html.P(v, className='value-stats')
                        ],
                        className='stat-card',
                        justify='center'
                    )
                    for k,v in dict_stats.items()
                ],
                gap=4
            )
        ],
    )
    return stats

def df_to_heatmap(df):
    #Create the heatmap graph
    fig = px.imshow(
        df,
        labels=dict(x='Time', y='Day', color='Number of songs listened', title='Listening activity heatmap'),
        color_continuous_scale='inferno',
        height=400)
    fig.update_layout(
        yaxis = dict(
            tickmode = 'array',
            tickvals = [*range(0, 7, 1)],
            ticktext = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],
            zeroline = False,
            showline = False,
            showgrid = False,
        ),
        xaxis = dict(
            tickmode = 'array',
            tickvals = [*range(0, 24, 1)],
            ticktext = ['12AM','1AM','2AM','3AM','4AM','5AM','6AM','7AM','8AM','9AM',
                        '10AM','11AM','12PM','1PM','2PM','3PM','4PM','5PM','6PM','7PM',
                        '8PM','9PM','10PM','11PM'],
            zeroline = False,
            showline = False,
            showgrid = False
        ),
        font_color='white',
        title_font_color='white',
        paper_bgcolor='rgb(39,38,38)',
        plot_bgcolor='rgb(0,0,0)',
        margin=dict(t=20,b=20,l=20,r=20),
    )
    fig.update(data=[{'customdata': df,
        'hovertemplate':
            '<br><b>Day </b>: %{y}'+
            '<br><b>Time </b>: %{x}'+
            '<br><b>Count </b>: %{z}<br>'+
            '<extra></extra>',
    }])
    return fig

def heatmap_yearly():
    #Create a matrix dataframe with the number of tracks played per hour (rows) and day of the week (columns)
    df = spotify_df.copy()
    df['endTime'] = pd.to_datetime(df['endTime'], format='%Y-%m-%d %H:%M')
    df['hour'] = df['endTime'].dt.hour
    df['day'] = df['endTime'].dt.dayofweek
    heatmap = df.groupby(['day', 'hour']).count()
    heatmap.reset_index(inplace=True)
    heatmap = heatmap[['day', 'hour', 'trackName']]
    heatmap.rename(columns={'trackName': 'Number of songs listened'}, inplace=True)
    heatmap.sort_values(by=['day', 'hour'], inplace=True)
    heatmap.reset_index(inplace=True)
    heatmap.drop(columns='index', inplace=True)
    heatmap = heatmap.pivot(index='day', columns='hour', values='Number of songs listened')
    return heatmap

def heatmap_weekly():
    df = spotify_df.copy()
    df['endTime'] = pd.to_datetime(df['endTime'], format='%Y-%m-%d %H:%M')
    df['hour'] = df['endTime'].dt.hour
    df['day'] = df['endTime'].dt.dayofweek
    df['week'] = df['endTime'].dt.isocalendar().week
    heatmap = df.groupby(['week', 'day', 'hour']).count()
    heatmap.reset_index(inplace=True)
    heatmap = heatmap[['week', 'day', 'hour', 'trackName']]
    heatmap.rename(columns={'trackName': 'Number of songs listened'}, inplace=True)
    heatmap.sort_values(by=['week', 'day', 'hour'], inplace=True)
    heatmap.reset_index(inplace=True)
    heatmap.drop(columns='index', inplace=True)
    heatmap = heatmap.fillna(0)
    week_list = heatmap['week'].astype(str).unique().tolist()

    def pivot_df(df):
        df = df.copy()
        df = df.pivot(index='day', columns='hour', values='Number of songs listened')
        df.reset_index(inplace=True)
        return df

    #Create a list of dataframes, one for each week of the year
    heatmap_list = [pivot_df(heatmap[heatmap['week'] == week]) for week in heatmap['week'].unique()]
    #Create a list containing heatmap figures for each week of the year
    json_list = [df.to_json(date_format='iso', orient='split') for df in heatmap_list]
    return json_list

def top_artists_bar_graph():
    df = spotify_df.copy()
    top_artists = df.groupby('artistName').sum()
    top_artists.reset_index(inplace=True)
    top_artists = top_artists[['artistName', 'msPlayed']]
    top_artists['msPlayed'] = top_artists['msPlayed'] / 60000
    top_artists['msPlayed'] = top_artists['msPlayed'].round()
    top_artists.rename(columns={'msPlayed': 'Minutes Listened'}, inplace=True)
    top_artists.sort_values(by='Minutes Listened', ascending=False, inplace=True)
    top_artists.reset_index(inplace=True)
    top_artists.drop(columns='index', inplace=True)
    top_artists = top_artists.head(15)
    colors = [
        '#b7193f', '#bc243f', '#c13040', '#c63b41', '#cb4741',
        '#cb4741', '#d45e42','#d96942', '#de7443', '#e38044',
        '#e88b44', '#ed9745', '#ed9745', '#ed9745', '#ed9745'
    ]

    fig = go.Figure(data=[go.Bar(
        x=top_artists['Minutes Listened'],
        y=top_artists['artistName'],
        marker_color=colors,
        orientation='h',
        hovertemplate =
            '<br><b>Artist Name </b>: %{y}'+
            '<br><b>Minutes listened </b>: %{x}<br>'+
            '<extra></extra>',
    )])
    fig.update_layout(
        title_text='Top artists',
        paper_bgcolor='rgb(39,38,38)',
        plot_bgcolor='rgb(39,38,38)',
        yaxis = dict(
            zeroline = False,
            showline = False,
            showgrid = False,
            side = 'right'
        ),
        xaxis = dict(
            zeroline = False,
            showline = False,
            showgrid = False
        ),
        font_color='white',
        title_font_color='white',
        margin=dict(t=25,b=20,l=20,r=20),
    )
    fig.update_traces(marker=dict(line=dict(width=0)))
    fig.update_xaxes(title_text='Minutes Listened')
    return fig

def top_tracks_bar_graph():
    df = spotify_df.copy()
    top_tracks = df.groupby(['artistName', 'trackName']).sum()
    top_tracks.reset_index(inplace=True)
    top_tracks = top_tracks[['artistName', 'trackName', 'msPlayed']]
    top_tracks['msPlayed'] = top_tracks['msPlayed'] / 60000
    top_tracks['msPlayed'] = top_tracks['msPlayed'].round()
    top_tracks.rename(columns={'msPlayed': 'Minutes Listened'}, inplace=True)
    top_tracks.sort_values(by='Minutes Listened', ascending=False, inplace=True)
    top_tracks.reset_index(inplace=True)
    top_tracks.drop(columns='index', inplace=True)
    top_tracks = top_tracks.head(15)

    #Create the graph with the artist with most listened minutes on top
    colors = [
        '#DF3226', '#E54428', '#E53123', '#EB3752', '#F5517B',
        '#F85F89', '#F96998','#F075AF', '#E770AD', '#DF6DB8',
        '#D56ABE', '#C56AC0', '#9870BF', '#8974BB', '#6C75BB'
    ]

    fig = go.Figure(data=[go.Bar(
        x=top_tracks['Minutes Listened'],
        y=top_tracks['trackName'],
        marker_color=colors,
        orientation='h',
        hovertemplate =
            '<br><b>Artist Name </b>: %{hovertext}'+
            '<br><b>Track </b>: %{y}'+
            '<br><b>Minutes listened </b>: %{x}<br>'+
            '<extra></extra>',
        hovertext = top_tracks['artistName'],
        showlegend = False,
    )])
    fig.update_layout(
        title_text='Top tracks',
        paper_bgcolor='rgb(39,38,38)',
        plot_bgcolor='rgb(39,38,38)',
        yaxis = dict(
            zeroline = False,
            showline = False,
            showgrid = False,
            side = 'right'
        ),
        xaxis = dict(
            zeroline = False,
            showline = False,
            showgrid = False
        ),
        font_color='white',
        title_font_color='white',
        margin=dict(t=25,b=20,l=20,r=20),
    )
    fig.update_traces(marker=dict(line=dict(width=0)))
    fig.update_xaxes(title_text='Minutes Listened')
    return fig

#App Layout Components
header = html.P(
    [
        'Spotify Dashboard ',
        html.A(
            '(by Francisco Nava)',
            href='https://github.com/grimhood/',
            target='_blank',
            className='link-header'
        )
    ],
    className='app-header'
)

tracks_range_radio = html.Div(
    [
        dcc.RadioItems(['Last 4 Weeks', 'Last 6 Months','All Time'],
        'Last 4 Weeks',
        id='tracks-range-radio',
        className='horizontal-radio')
    ],
    className='radio-container',
)

profile_image = html.Div(html.Img(src = app.get_asset_url('profile.jpg'), className='profile-image'), className='profile-image-container')
profile_image = html.Div(
    [
        html.A(
            html.Img(src = app.get_asset_url('profile.jpg'), className='profile-image'),
            href='https://open.spotify.com/user/1277049780',
            target='_blank'
        )
    ],
    className='profile-image-container'
)
card_top_tracks = html.Div([], id='top-tracks')
card_recent_tracks = html.Div([recent_tracks()], id='recent-tracks')
card_user_stats = html.Div(user_stats())

navbar = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink('Overview', active= 'exact', href='/overview/')),
        dbc.NavItem(dbc.NavLink('Listening Patterns', active= 'exact', href='/listening_patterns/')),
        dbc.NavItem(dbc.NavLink('Top Tracks & Artists', active= 'exact', href='/top/')),
        dbc.NavItem(dbc.NavLink('About', active= 'exact', href='/about/')),
    ],
    vertical='lg',
    pills=True,
    fill=True,
)
navbar_container = dbc.Col([navbar], width=1, className='column-container')
dropdown_options = [{'label': f'Week {x}', 'value': x} for x in range(0, 53)]
dropdown_week = html.Div([dcc.Dropdown(options=dropdown_options, value=0, id='dropdown-week', maxHeight=150)])
control_title = html.H4('Select', className='section-header')
navbar_container_dropdown = dbc.Col(
    className='column-container',
    width=1,
    children=[
        html.Div(
            [
                dbc.Col([navbar])
            ]
        ),
        html.Div(
            [
                dbc.Col([control_title, dropdown_week], className='controls')
            ],
        )
    ]
)

content = dbc.Container(
    children=[
            dbc.Row(
                [
                    dbc.Col([header])
                ],
                justify='center'
            ),
            dbc.Row(
                [
                    navbar_container
                ],
                id='page-content',
                justify='center', 
            ),
    ],
    className='dbc',
    fluid=True,
)

dcc.Location(id='url'),

about = html.Div(
        [
            html.P("Have you ever wondered what are your personal listening patterns?"),
            html.P("You can now engage with this dashboard to get to know, understand and visualize my favorite music."),
            html.P("From a personal overview, to listening patterns, and top tracks/artists."),
            html.Br(),
            html.Br(),
            html.P('Here, I present you my personal Spotify dashboard, an interactive web application built'),
            html.P("using Spotify's API data obtained via Python, transformed using Pandas and visualized with Plotly Dash."),
            html.P(["The application is hosted on Render and the code is available on my ", html.A("Github.", href='https://github.com/grimhood/', target='_blank',)]),
            html.Br(),
            html.P("I hope you enjoy it!"),
        ],
        className='about-section'

)

links = html.Div(
    [
        #Make a link with an icon to its left
        html.Div(
            [
                dbc.Button(
                    [
                        html.I(className='fas fa-envelope-square'),
                        html.Span(' Email'),
                    ],
                    href='mailto:f.nava.morales92@gmail.com',
                    target='_blank',
                ),
            ],
            className='social-link',
        ),
        html.Div(
            [
                dbc.Button(
                    [
                        html.I(className='fa brands fa-github-alt'),
                        html.Span(' Github'),
                    ],
                    href='https://github.com/grimhood/',
                    target='_blank',
                ),
            ],
            className='social-link',
        ),
        html.Div(
            [
                dbc.Button(
                    [
                        html.I(className='fab fa-linkedin'),
                        html.Span(' LinkedIn'),
                    ],
                    href='https://www.linkedin.com/in/navamorales/',
                    target='_blank',
                ),
            ],
            className='social-link',
        ),
    ]
)


#App Layout
app.layout = dbc.Container(
    [
        html.Div(id='dummy'),
        dcc.Location(id='url'),
        dcc.Store(id='stored-window-size'),
        dcc.Store(id='stored-heatmap-yearly'),
        dcc.Store(id='stored-heatmap-weekly'),
        content
    ],
    className='dbc',
    fluid=True,
    id='main-container',
)

#Client-Side callbacks
#––––––––––––––––––––––––––––––––––––––––––––––––––
#Sets zoom of the layout depending on the browser window size
app.clientside_callback(
    """
    function(href) {
        var window_height = window.innerHeight;
        return [window_height]
    }
    """,
    Output('stored-window-size','data'),
    Input('url', 'href'),
)


#Callbacks
@app.callback(
    Output('stored-heatmap-yearly', 'data'),
    Input('dummy', 'children'),
)
def store_heatmap_data_yearly_callback(dummy):
    df = heatmap_yearly().to_json(date_format='iso', orient='split')
    return df

@app.callback(
    Output('stored-heatmap-weekly', 'data'),
    Input('dummy', 'children'),
)
def store_heatmap_data_weekly_callback(dummy):
    df = heatmap_weekly()
    return df

@app.callback(
    Output('top-tracks', 'children'),
    Input('tracks-range-radio', 'value'),
)
def top_tracks_callback(value):
    if value:
        return top_tracks(value)
    else:
        raise PreventUpdate
    
@app.callback(
    Output('listening-patterns-yearly', 'children'),
    Input('stored-window-size', 'data'),
    Input('stored-heatmap-yearly', 'data'),
)
def listening_patterns_yearly_callback(window_size, heatmap_yearly_json):
    title1=html.H4('Yearly listening patterns', className='section-header section-header-heatmap')
    height = window_size[0] *0.35
    fig_yearly = pd.read_json(heatmap_yearly_json, orient='split').copy()
    fig_yearly = df_to_heatmap(fig_yearly)
    fig_yearly.update_layout(height=height)
    listening_patterns_yearly = html.Div([dcc.Graph(figure=fig_yearly)], className='heatmap')
    return [title1, listening_patterns_yearly]

@app.callback(
    Output('listening-patterns-weekly', 'children'),
    Input('stored-window-size', 'data'),
    Input('stored-heatmap-weekly', 'data'),
    Input('dropdown-week', 'value'),
)
def listening_patterns_weekly_callback(window_size, heatmap_weekly_json, week):
    title=html.H4(f'Weekly listening patterns (Week {week})', className='section-header section-header-heatmap')
    height = window_size[0] *0.35
    heatmap_df = pd.read_json(heatmap_weekly_json[week], orient='split').copy()
    fig = df_to_heatmap(heatmap_df)
    fig.update_layout(height=height)
    listening_patterns_weekly = html.Div([dcc.Graph(figure=fig)], className='heatmap')
    return [title, listening_patterns_weekly]

@app.callback(
    Output('top-artists-tracks', 'children'),
    Input('stored-window-size', 'data'),
)
def top_artists_tracks_callback(window_size):
    height = window_size[0] *0.40
    top_artists_fig = top_artists_bar_graph()
    top_tracks_fig = top_tracks_bar_graph()
    top_artists_fig.update_layout(height=height)
    top_tracks_fig.update_layout(height=height)
    return [
        html.Div([dcc.Graph(figure=top_tracks_fig)], className='heatmap'),
        html.Div([dcc.Graph(figure=top_artists_fig)], className='heatmap')
    ]

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')],
)
def render_page_content(pathname):
    landing_pathnames = ['/','/overview/']
    if pathname in landing_pathnames:
        return [
            navbar_container,
            dbc.Col([card_recent_tracks], width=2, className='column-container'),
            dbc.Col([card_top_tracks, tracks_range_radio], width=4, className='column-container'),
            dbc.Col([profile_image, card_user_stats], width=2, className='column-container')
        ]
    elif pathname == '/listening_patterns/':
        return [
            navbar_container_dropdown,
            dbc.Col(
                [
                    html.Div(id='listening-patterns-yearly'),
                    dbc.Spinner(html.Div(id='listening-patterns-weekly'), color="primary")
                ],
                width=8,
                className='column-container'
            )
        ]
    elif pathname == '/top/':
        return [
            navbar_container,
            dbc.Col([dbc.Spinner(html.Div(id='top-artists-tracks'), color="primary")], width=8, className='column-container')
        ]
    elif pathname == '/about/':
        return [
            navbar_container,
            dbc.Col([about], width=5, className='column-container'),
            dbc.Col([profile_image, links], width=2, className='column-container')
        ]
    # If the user tries to reach a different page, return a 404 message
    # return dbc.Jumbotron(
    #     [
    #         html.H1('404: Not found', className='text-danger'),
    #         html.Hr(),
    #         html.P(f'The pathname {pathname} was not recognised...'),
    #     ]
    # )


if __name__ == '__main__':
    app.run(debug=True)