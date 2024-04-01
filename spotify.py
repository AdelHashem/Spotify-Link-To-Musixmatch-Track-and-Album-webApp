import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
import requests
import redis
from os import environ
import logging

class Spotify:
    def __init__(self, client_id=None, client_secret=None) -> None:
        self.client_id = client_id if client_id else environ.get("SPOTIPY_CLIENT_ID")
        self.client_secret = client_secret if client_secret else environ.get("SPOTIPY_CLIENT_SECRET")
        if not (self.client_id and self.client_secret):
            self.RRAuth()
        else:
            cred = SpotifyClientCredentials(self.client_id, self.client_secret)
            self.sp = spotipy.Spotify(client_credentials_manager=cred,retries= 3 )
        self.session = requests.Session()
        # if client_id is not None:

    def RRAuth(self):
        r = redis.Redis(
        host=environ.get("REDIS_HOST"),
        port=environ.get("REDIS_PORT"),
        password=environ.get("REDIS_PASSWD"))

        doc = r.json().get("spotify","$")
        doc = doc[0]
        cred = doc["cred"][doc["rr"]]
        logging.info(f"Spotify Cred: {cred}")
        r.json().set("spotify","$.rr",(doc["rr"]+1)%len(doc["cred"]))
        r.close()
        cred = SpotifyClientCredentials(cred[0], cred[1])
        self.sp = spotipy.Spotify(client_credentials_manager=cred,retries= 3 )

    def get_tarck(self, link=None, track=None) -> dict:
        if link is not None: track = self.get_spotify_id(link)
        return self.sp.track(track)

    def get_album_tarck(self, id: str) -> dict:
        return self.sp.album_tracks(id)

    def get_tracks(self, ids) -> list:
        return self.sp.tracks(ids)["tracks"]

    def get_isrc(self, link):
        if not (self.client_id and self.client_secret):
            self.RRAuth()
        isrcs = []
        track = None
        match =re.search(r'spotify.link/\w+', link)
        if match:
            link = self.session.get(link).url

        match = re.search(r'album/(\w+)', link)
        if match:
            tracks = self.get_album_tarck(match.group(1))
            link = None
            ids = [temp["id"] for temp in tracks["items"]]
            tracks = self.get_tracks(ids)

            for i in tracks:
                if "external_ids" in i:
                    try:
                        image = i["album"]["images"][1]["url"]
                    except:
                        image = None

                    if i["external_ids"].get("isrc"):
                        isrcs.append({"isrc": i["external_ids"]["isrc"], "image": image, "track": i})
                    else:
                        isrcs.append("The Track is missing its ISRC on Spotify.")
                else:
                    return "Error in get_isrc"

            return isrcs

        else:
            track = self.get_tarck(link, track)
            print(link)
            if "external_ids" in track:
                img = track["album"]["images"][1]["url"]
                isrcs.append({"isrc": track["external_ids"]["isrc"], "image": img, "track": track})
                return isrcs
            else:
                return "Error in get_isrc"

    def artist_albums(self, link, albums=[], offset=0) -> list:
        data = self.sp.artist_albums(link, limit=50, offset=offset, album_type="album,single,compilation")
        offset = offset + 50
        albums.extend(data["items"])
        if data["next"]:
            return self.artist_albums(link, albums, offset)
        else:
            return albums

    def get_spotify_id(self, link):
        match = re.search(r'track/(\w+)', link)
        if match:
            return match.group(1)
        elif re.search(r'artist/(\w+)', link):
            return re.search(r'track/(\w+)', link).group(1)

        else:
            return None

    def search_by_isrc(self, isrc):
        data = self.sp.search(f"isrc:{isrc}")
        if data["tracks"]["items"]:
            track = data["tracks"]["items"][0]
            if isrc == track["external_ids"]["isrc"]:
                img = track["album"]["images"][1]["url"]
                return [{"isrc": track["external_ids"]["isrc"], "image": img, "track": track}]
        return ["No track found with this ISRC"]
