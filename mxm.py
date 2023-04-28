import requests,time
from urllib3.util.retry import Retry
import os


class MXM:
    BASE_URL = "https://api.musixmatch.com/ws/1.1/"
    DEFAULT_KEY = os.environ.get("MXM_API")

    def __init__(self, key=None):
        self.key = key or self.DEFAULT_KEY
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[ 500, 502, 503, 504 ])
        self.session.mount('http://', requests.adapters.HTTPAdapter(max_retries=retries))
        self.session.mount('https://', requests.adapters.HTTPAdapter(max_retries=retries))

    def __del__(self):
        if isinstance(self.session, requests.Session):
            self.session.close()

    def change_key(self, key):
        self.key = key

    def track_get(self, isrc = None, commontrack_id = None) -> dict:
        url = f"{self.BASE_URL}track.get"
        params = {"track_isrc": isrc, "commontrack_id":commontrack_id, "apikey": self.key}
        response = self.session.get(url, params=params)
        try:
            response.raise_for_status()
            data = response.json()
            status_code = data["message"]["header"]["status_code"]
            if status_code == 200:
                return data
            elif status_code == 401:
                return "Invalid or missing API key"
            elif status_code == 402:
                return "Usage limit has been reached. Try another API key."
            elif status_code == 403:
                return "You are not authorized to perform this operation"
            elif status_code == 404:
                return 404
                #return "The requested resource was not found. The track hasn't been imported yet."
        except requests.exceptions.HTTPError as e:
            return f"HTTP error occurred: {e}"
        except:
            return "Error in MXM API"
        
    def matcher_track(self,sp_id):
        url = f"{self.BASE_URL}matcher.track.get"
        params = {"track_spotify_id": sp_id, "q_album": "None", "q_artist": "None", "q_track": "None", "apikey": self.key}
        response = self.session.get(url, params=params)
        try:
            response.raise_for_status()
            data = response.json()
            status_code = data["message"]["header"]["status_code"]
            if status_code == 200:
                return data
            elif status_code == 401:
                return "Invalid or missing API key"
            elif status_code == 402:
                return "Usage limit has been reached. Try another API key."
            elif status_code == 403:
                return "You are not authorized to perform this operation"
            elif status_code == 404:
                return 404
                #return "The requested resource was not found. The track hasn't been imported yet."
        except requests.exceptions.HTTPError as e:
            return f"HTTP error occurred: {e}"
        except:
            return "Error in MXM API"

        
    def Track_links(self, isrc):
        track = self.track_get(isrc)
        try:
            id = track["message"]["body"]["track"]["commontrack_id"]
        except TypeError:
            return track
        track_url = track["message"]["body"]["track"]["track_she_url"]
        album_id = track["message"]["body"]["track"]["album_id"]

        album_url = f"https://www.musixmatch.com/album/id/{album_id}"
        return [id, track_url, album_url]

    def Tracks_Data(self, iscrcs):
        tracks = []
        Limit = 5
        import_count = 0
        if "isrc" not in iscrcs[0]:
            return iscrcs
        
        if iscrcs[0].get("track"):
            matcher = self.matcher_track(iscrcs[0]["track"]["id"])

        for i in iscrcs:
            track = self.track_get(i["isrc"])

            # try to import the track
            if track == 404:
                
                if import_count < Limit:
                    import_count +=1
                    self.matcher_track(i["track"]["id"])
                    time.sleep(1)
                    track = self.track_get(i["isrc"])
                if track == 404:
                    track = self.matcher_track(i["track"]["id"])
            if track == 404:
                track = "The track hasn't been imported yet. Try one more time after a minute (tried to import it using matcher call)."
                tracks.append(track)
                continue
            
            try:
                track = track["message"]["body"]["track"]
                track["isrc"] = i["isrc"]
                track["image"] = i["image"]
                try:
                    track["matcher_album"] = [matcher["message"]["body"]["track"]["album_id"], matcher["message"]["body"]["track"]["album_name"]]
                except:
                    pass
                

                tracks.append(track)
            except (TypeError, KeyError):
                tracks.append(track)
            time.sleep(.1)
        return tracks
