import re
import requests
import base64
from pathlib import Path


class Spotify:

    auth = "OThmNmVlNzk5ZjRkNDYwMDhlZGI4MjI4OWQwY2UyNDQ6ZGM0NGUxYmExMTlmNDMxNDlhMTQxZTU4NGUzNDE5ZmU="
    token = ""

    def __init__(self, client_id=None, client_secret=None) -> None:
        if client_id != None:
            self.ChangeAuth(self, client_id, client_secret)

    def ChangeAuth(self, client_id, client_secret):
        auth_str = f'{client_id}:{client_secret}'
        self.auth = base64.urlsafe_b64encode(auth_str.encode()).decode()

    def get_token(self):
        url = 'https://accounts.spotify.com/api/token'
        payload = {
            'grant_type': 'client_credentials'
        }

        headers = {
            'Authorization': f'Basic {self.auth}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        try:
            self.token = response.json()['access_token']
        except:
            print("Error Getting Token")
        
        return response.json()['access_token']

    def get_tarck(self, link: str) -> dict:
        track = self.get_spotify_id(link)
        url = f"https://api.spotify.com/v1/tracks/{track}"

        payload = {}
        headers = {
            'authority': 'api.spotify.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
            'authorization': f'Bearer {self.token}',
            'content-type': 'application/json',
            'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        return response.json()

    def get_isrc(self,link):
        self.get_token()
        track = self.get_tarck(link)
        if "external_ids" in track:
            return track["external_ids"]["isrc"]
        else:
            return "Error in get_isrc"

    def get_spotify_id(self,link):
        match = re.search(r'track/(\w+)', link)
        if match:
            return match.group(1)
        else:
            return None
