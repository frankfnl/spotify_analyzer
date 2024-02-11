
import json
import os
import requests
from datetime import date
from refresh import Refresh

class GetTopStats:
    def __init__(self):
        self.spotify_token = ""
        self.tracks = {}

    def get_top_tracks(self, time_range='medium_term', limit=20):
        url = f"https://api.spotify.com/v1/me/top/tracks?time_range={time_range}&limit={limit}"
        
        response = requests.get(url, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.spotify_token}"
        })

        response_json = response.json()

        for track in response_json['items']:
            self.tracks[track['uri']] = track['name']

        for key in self.tracks:
            print(self.tracks[key])
        
    def call_refresh(self):
        """Calls the refresh method from the Refresh class"""	
        refreshCaller = Refresh()
        self.spotify_token = refreshCaller.refresh()
        self.get_top_tracks()
        
a = GetTopStats()
a.call_refresh()