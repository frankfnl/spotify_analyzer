import os
import requests
import json
from dotenv import load_dotenv

#Load environment variables
load_dotenv()
client_id = os.environ['client_id']
client_secret = os.environ['client_secret']
redirect_uri = os.environ['redirect_uri']
refresh_token = os.environ['refresh_token']
base_64 = os.environ['base_64']

class Refresh:

    def __init__(self):
        self.refresh_token = refresh_token
        self.base_64 = base_64

    def refresh(self):

        query = "https://accounts.spotify.com/api/token"

        response = requests.post(
            query,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            },
            headers={
                "Authorization": "Basic " + base_64
            }
        )

        response_json = response.json()
        return response_json["access_token"]


a = Refresh()
a.refresh()
