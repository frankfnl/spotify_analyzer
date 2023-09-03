import pandas as pd
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()
sp_auth = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

#Function to read a json file using pandas
def read_json(file_path):
    df = pd.read_json(file_path)
    return df

#Function to stack together two dataframes with the same columns
def stack_dfs(df1, df2):
    df = pd.concat([df1, df2])
    return df

#Function to stack together n number of dataframes with the same columns
def stack_n_dfs(df_list):
    df = pd.concat(df_list)
    return df

#Function to get removed duplicates from a dataframe based on two column names
def remove_duplicates(df, col1, col2):
    df.drop_duplicates(subset=[col1, col2], inplace=True)
    df.reset_index(inplace=True)
    return df

#Function to get the track ID from Spotofy API, given the track name and artist name
def get_track_id(track_name, artist_name, sp_auth):
    try:
        track_id = sp_auth.search(q=f'track:{track_name} artist:{artist_name}', type='track')['tracks']['items'][0]['id']
        return track_id
    except:
        return 'ID not found'

#Function to create a new column in a dataframe with the track ID
def add_track_id(csv_filename, sp_auth):
    df = pd.read_csv(csv_filename)
    df['trackID'] = df.apply(lambda x: get_track_id(x['trackName'], x['artistName'], sp_auth), axis=1)
    df.to_csv(csv_filename, index=False)
    return df

#Function to get the audio features of a track from Spotify API, given the track ID
def get_audio_features(track_id, sp_auth):
    try:
        audio_features = sp_auth.audio_features(track_id)[0]
        return audio_features
    except:
        return 'Audio features not found'

#Function to create new columns in a dataframe with the audio features of a track (one column for each feature)
def add_audio_features(csv_filename, sp_auth):
    audio_features = [
        'danceability',
        'energy',
        'key',
        'loudness',
        'mode',
        'speechiness',
        'acousticness',
        'instrumentalness',
        'liveness',
        'valence',
        'tempo',
        'time_signature'
    ]

    df = pd.read_csv(csv_filename)
    df['audioFeatures'] = df.apply(lambda x: get_audio_features(x['trackID'], sp_auth), axis=1)
    for feature in audio_features:
        df[feature] = df.apply(lambda x: x['audioFeatures'][feature] if x['audioFeatures']not in ['Audio features not found', None] else '', axis=1)
    df.drop(columns=['audioFeatures'], inplace=True)
    df.to_csv(csv_filename, index=False)
    return df

#function to split a dataframe into smaller dataframes and save them as csv files
def split_df(df, n):
    df_list = [df[i:i+n] for i in range(0,df.shape[0],n)]
    for i in range(len(df_list)):
        df_list[i].to_csv(f'spotify_data/enriched_data/df_{i}.csv', index=False)
    return df_list

#Function to get the top 10 artists from a dataframe
def top_artists(df):
    top_artists = df.groupby('artistName').count().sort_values(by='endTime', ascending=False).head(10)
    return top_artists

#Function to get the top 10 tracks from a dataframe
def top_tracks(df):
    top_tracks = df.groupby(['artistName', 'trackName']).count().sort_values(by='endTime', ascending=False).head(10)
    top_tracks.rename(columns={'endTime': 'PlayCount'}, inplace=True)
    top_tracks.drop(columns='msPlayed', inplace=True)
    top_tracks.reset_index(inplace=True)
    return top_tracks

#Function to get the number of times a track has been played
def track_count(df, track_name):
    track_count = df.groupby('trackName').size()[track_name]
    return track_count

#Data wrangling
#streaming1 = read_json('spotify_data/StreamingHistory0.json')
#streming2 = read_json('spotify_data/StreamingHistory1.json')
#streaming_df = stack_dfs(streaming1, streming2)
# print(streaming_df.head())
# print(streaming_df.shape)
# print(top_artists(streaming_df))
# print(top_tracks(streaming_df))
#no_duplicates_df = remove_duplicates(streaming_df, 'trackName', 'artistName')
#print(no_duplicates_df.shape)
#split_df(no_duplicates_df, 50)


#Apply add_track_id function to only the first 3 dataframes in spotify_data/enriched_data
# for i in range(30,105):
#     import time
#     #wait 1 minute every 5 files
#     if i % 5 == 0:
#         print('Waiting 1 minute...')
#         time.sleep(40)
#         print(f'Processing df_{i}.csv')
#         add_audio_features(f'spotify_data/enriched_data/df_{i}.csv', sp_auth)
#     else:
#         print(f'Processing df_{i}.csv')
#         time.sleep(5)
#         add_audio_features(f'spotify_data/enriched_data/df_{i}.csv', sp_auth)

#add_track_id(no_duplicates_df, sp_auth)

#Calculate various interesting statistics from the dataframe
# total_time = streaming_df['msPlayed'].sum()
# total_time_hours = total_time / 3600000
# total_time_days = total_time_hours / 24
# total_time_weeks = total_time_days / 7
# total_time_years = total_time_weeks / 52
# total_tracks = streaming_df.shape[0]
# total_artists = streaming_df['artistName'].nunique()
# total_playlists = streaming_df['trackName'].nunique()

list_dfs = [pd.read_csv(f'spotify_data/enriched_data/df_{i}.csv') for i in range(0,105)]
streaming_df = stack_n_dfs(list_dfs)
streaming_df.to_csv('spotify_data/streaming_history.csv', index=False)
print(streaming_df.shape)