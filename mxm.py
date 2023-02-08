import requests

class MXM:
    key = "41b9b3af66092b9d785e30fac520e308"

    def changeKey(self,key):
        self.key = key

    def Track_Get(self,isrc) -> dict:
        url = f"http://api.musixmatch.com/ws/1.1/track.get?track_isrc={isrc}&apikey={self.key}"
        response = requests.request("GET", url)
        try:
            status = response.json()
            status = status["message"]["header"]["status_code"]
            
            if status == 200: return response.json()
            elif status == 401: return "invalid/missing API key"
            elif status == 402: return "The usage limit has been reached. Try to use another api key"
            elif status == 403: return "You are not authorized to perform this operation"
            elif status == 404: return "The requested resource was not found.</br>The track hasn't been imported yet." 
        except:
            return "Error in MXM API "

    def Track_links(self,isrc):
        track = self.Track_Get(isrc)
        try:
            id = track["message"]["body"]["track"]["commontrack_id"]
        except TypeError:
            return track
        track_url = track["message"]["body"]["track"]["track_share_url"]
        album_id = track["message"]["body"]["track"]["album_id"]
        album_url = f"https://www.musixmatch.com/album/id/{album_id}"
        return [id,track_url,album_url]
