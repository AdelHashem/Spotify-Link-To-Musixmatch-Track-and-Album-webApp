import time
import os
import mxmapi
import re


class MXM:
    DEFAULT_KEY = os.environ.get("MXM_API")

    def __init__(self, key=None):
        self.key = key or self.DEFAULT_KEY
        self.musixmatch = mxmapi.Musixmatch(self.key)

    def change_key(self, key):
        self.key = key

    def track_get(self, isrc=None, commontrack_id=None) -> dict:
        try:
            response = self.musixmatch.track_get(
                track_isrc=isrc, commontrack_id=commontrack_id
            )
            return response
        except mxmapi.exceptions.MXMException as e:
            if re.search("404", str(e)):
                return 404
            else:
                return e

    def matcher_track(self, sp_id):
        try:
            response = self.musixmatch.matcher_track_get(
                q_track="null", track_spotify_id=sp_id
            )
            return response
        except mxmapi.exceptions.MXMException as e:
            if re.search("404", str(e)):
                return 404
            else:
                return e

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
        k = 0
        for i in iscrcs:
            track = self.track_get(i["isrc"])

            # try to import the track
            if track == 404:
                if import_count < Limit:
                    import_count += 1
                    track = self.matcher_track(i["track"]["id"])
                    if isinstance(track, mxmapi.exceptions.MXMException):
                        tracks.append(track)
                        continue
                    track = self.track_get(i["isrc"])
            if track == 404:
                track = "The track hasn't been imported yet. Try one more time after a minute (tried to import it using matcher call)."
                tracks.append(track)
                continue

            try:
                track = track["message"]["body"]["track"]
                track["isrc"] = i["isrc"]
                track["image"] = i["image"]
                try:
                    if (
                        k == 0
                        and track["commontrack_id"]
                        == matcher["message"]["body"]["track"]["commontrack_id"]
                    ):
                        track["matcher_album"] = [
                            matcher["message"]["body"]["track"]["album_id"],
                            matcher["message"]["body"]["track"]["album_name"],
                        ]
                        k += 1
                except:
                    pass

                tracks.append(track)
            except (TypeError, KeyError):
                tracks.append(track)
            time.sleep(0.1)

        print(tracks)
        return tracks
