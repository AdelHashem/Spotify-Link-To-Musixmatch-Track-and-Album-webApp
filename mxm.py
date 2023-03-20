import requests,time

class MXM:
    BASE_URL = "http://api.musixmatch.com/ws/1.1/"
    DEFAULT_KEY = "41b9b3af66092b9d785e30fac520e308"

    def __init__(self, key=None):
        self.key = key or self.DEFAULT_KEY
        self.session = requests.Session()

    def change_key(self, key):
        self.key = key

    def track_get(self, isrc) -> dict:
        url = f"{self.BASE_URL}track.get"
        params = {"track_isrc": isrc, "apikey": self.key}
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
                return "The requested resource was not found. The track hasn't been imported yet."
        except requests.exceptions.HTTPError as e:
            return f"HTTP error occurred: {e}"
        except:
            return "Error in MXM API"

    def Track_links(self,isrc):
        track = self.track_get(isrc)
        try:
            id = track["message"]["body"]["track"]["commontrack_id"]
        except TypeError:
            return track
        track_url = track["message"]["body"]["track"]["track_she_url"]
        album_id = track["message"]["body"]["track"]["album_id"]

        album_url = f"https://www.musixmatch.com/album/id/{album_id}"
        return [id,track_url,album_url]
    


    def Tracks_Data(self,iscrcs):
        tracks = []
        if "isrc" not in iscrcs[0]: return iscrcs
        for i in iscrcs:
            track = self.track_get(i["isrc"])
            time.sleep(.1)
            try:
                track = track["message"]["body"]["track"]
                track["isrc"] = i["isrc"]
                track["image"] = i["image"]
                tracks.append(track)
            except (TypeError, KeyError):
                tracks.append(track)
        return tracks
        


        


