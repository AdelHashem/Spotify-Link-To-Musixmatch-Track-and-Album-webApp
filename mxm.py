import requests


class MXM:
    key = "41b9b3af66092b9d785e30fac520e308"

    def changeKey(self,key):
        self.key = key

    def Track_Get(self,isrc) -> dict:
        url = f"http://api.musixmatch.com/ws/1.1/track.get?track_isrc={isrc}&apikey={self.key}"
        response = requests.request("GET", url)
        if response.status_code == 200: return response.json()
        elif response.status_code == 401: print("invalid/missing API key")
        elif response.status_code == 402: print("The usage limit has been reached. Try to use another api key")
        elif response.status_code == 403: print("You are not authorized to perform this operation")
        elif response.status_code == 404: print("The requested resource was not found.")
        else: print("Ops. Something were wrong.")

    def Track_links(self,isrc):
        track = self.Track_Get(isrc)
        id = track["message"]["body"]["track"]["commontrack_id"]
        track_url = track["message"]["body"]["track"]["track_share_url"]
        album_id = track["message"]["body"]["track"]["album_id"]
        album_url = f"https://www.musixmatch.com/album/id/{album_id}"
        return [id,track_url,album_url]
