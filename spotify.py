import re
import requests
import base64
from pathlib import Path


class Spotify:

    BASE_URL = "https://api.spotify.com/v1/"
    auth = "OThmNmVlNzk5ZjRkNDYwMDhlZGI4MjI4OWQwY2UyNDQ6ZGM0NGUxYmExMTlmNDMxNDlhMTQxZTU4NGUzNDE5ZmU="
    token = ""

    def __init__(self, client_id=None, client_secret=None) -> None:
        self.session = requests.Session()
        if client_id is not None:
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

        response = self.session.post(url, headers=headers, data=payload)
        try:
            self.token = response.json()['access_token']
        except:
            print("Error Getting Token")
        
        return response.json()['access_token']

    def get_tarck(self, link = None,track = None) -> dict:
        if link is not None: track = self.get_spotify_id(link)
        url = f"{self.BASE_URL}tracks/{track}"

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
        response = self.session.get(url, headers=headers, data=payload)
        return response.json()


    def get_album_tarck(self, id: str) -> dict:
        #track = self.get_spotify_id(link)
        url = f"{self.BASE_URL}albums/{id}/tracks"

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
        response = self.session.get(url, headers=headers, data=payload)
        #print(response.json())
        #return response.json()["items"][0]["id"]
        return response.json()["items"]


    def get_isrc(self,link):
        isrcs = []
        count = 0
        self.get_token()
        track = None
        match = re.search(r'album/(\w+)', link)
        if match: 
            tracks = self.get_album_tarck(match.group(1))
            link = None

            for i in tracks:
                track_info = self.get_tarck(track =i["id"])
                if "external_ids" in track_info:
                    isrcs.append({"isrc":track_info["external_ids"]["isrc"],"image":track_info["album"]["images"][1]["url"] })
                else:
                    return "Error in get_isrc"
                
            return isrcs

        else:     
            track = self.get_tarck(link,track)
            if "external_ids" in track:
                img = track["album"]["images"][1]["url"]
                isrcs.append({"isrc": track["external_ids"]["isrc"], "image":img })
                return isrcs
            else:
                return "Error in get_isrc"

    def get_spotify_id(self,link):
        match = re.search(r'track/(\w+)', link)
        if match:
            return match.group(1)
        else:
            return None
