import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re, time
import requests
from pathlib import Path


class Spotify:
    def __init__(self, client_id=None, client_secret=None) -> None:
        client_id= '98f6ee799f4d46008edb82289d0ce244'
        client_secret= 'dc44e1ba119f43149a141e584e3419fe'

        cred = SpotifyClientCredentials(client_id,client_secret)
        self.sp = spotipy.Spotify(client_credentials_manager=cred)

        self.session = requests.Session()
        #if client_id is not None:
            #self.ChangeAuth(self, client_id, client_secret)

    def ChangeAuth(self, client_id, client_secret):
        cred = SpotifyClientCredentials(client_id,client_secret)
        self.sp = spotipy.Spotify(client_credentials_manager=cred)


    def get_tarck(self, link = None,track = None) -> dict:
        if link is not None: track = self.get_spotify_id(link)
        return self.sp.track(track)


    def get_album_tarck(self, id: str) -> dict:
        return self.sp.album_tracks(id)


    def get_isrc(self,link):
        isrcs = []
        track = None
        match = re.search(r'album/(\w+)', link)
        if match: 
            tracks = self.get_album_tarck(match.group(1))
            link = None

            for i in tracks["items"]:
                track_info = self.get_tarck(track =i["id"])
                if "external_ids" in track_info:
                    isrcs.append({"isrc":track_info["external_ids"]["isrc"],"image":track_info["album"]["images"][1]["url"] })
                else:
                    return "Error in get_isrc"
                time.sleep(0.03)
                
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
