import os
import re

import Asyncmxm 
import asyncio


class MXM:
    DEFAULT_KEY = os.environ.get("MXM_API")
    DEFAULT_KEY2 = os.environ.get("MXM_API2")

    def __init__(self, key=None, session=None):
        self.key = key or self.DEFAULT_KEY
        self.key2 = key or self.DEFAULT_KEY2
        self.session = session
        self.musixmatch = Asyncmxm.Musixmatch(self.key,requests_session=session)
        self.musixmatch2 = Asyncmxm.Musixmatch(self.key2,requests_session=session)

    def change_key(self, key):
        self.key = key

    async def track_get(self, isrc=None, commontrack_id=None) -> dict:
        try:
            response = await self.musixmatch.track_get(
                track_isrc=isrc, commontrack_id=commontrack_id
            )
            return response
        except Asyncmxm.exceptions.MXMException as e:
            return str(e)

    async def matcher_track(self, sp_id):
        try:
            response = await self.musixmatch2.matcher_track_get(
                q_track="null", track_spotify_id=sp_id
            )
            return response
        except Asyncmxm.exceptions.MXMException as e:
            return str(e)

    async def Track_links(self, sp_data):
        isrc = sp_data["isrc"]
        track = await self.track_get(isrc)
        try:
            id = track["message"]["body"]["track"]["commontrack_id"]
        except TypeError as e:
            return track

        track = track["message"]["body"]["track"]
        track["isrc"] = sp_data["isrc"]
        track["image"] = sp_data["image"]
        
        return track
    
    async def matcher_links(self, sp_data):
        id = sp_data["track"]["id"]
        track = await self.matcher_track(id)
        try:
            id = track["message"]["body"]["track"]["commontrack_id"]
        except TypeError as e:
            return track

        track = track["message"]["body"]["track"]
        track["isrc"] = sp_data["isrc"]
        track["image"] = sp_data["image"]
        return track

    async def Tracks_Data(self, sp_data):
        links = []
        tracks = await self.tracks_get(sp_data)
        if  sp_data[0].get("track"):
            matchers = await self.tracks_matcher(sp_data)
        else:
            return tracks

        for i in range(len(tracks)):
            track = tracks[i]
            matcher = matchers[i]

            if isinstance(track, dict) and isinstance(matcher, dict):
                if (
                        track["commontrack_id"]
                        == matcher["commontrack_id"]
                    ):
                        track["matcher_album"] = [
                            matcher["album_id"],
                            matcher["album_name"],
                        ]
                else: 
                    track["note"] = "This track may be facing an ISRC issue."
                links.append(track)
                continue

            elif isinstance(track, str) and isinstance(matcher, str):
                if re.search("404", track):
                    track = """
                    The track hasn't been imported yet. Please try again after 1-5 minutes. 
                    Sometimes it may take longer, up to 15 minutes, depending on the MXM API and their servers.
                    """
                    links.append(track)
                    continue
            elif isinstance(track, str) and isinstance(matcher, dict):
                if matcher.get("album_name") == sp_data[i]["track"]["album"]["name"]:
                    links.append(matcher)
                    continue
            elif isinstance(track, dict) and isinstance(matcher, str):
                track["note"] = "This track may missing its Spotify id"
                links.append(track)
            else:
                links.append(track)
        return links
    
    async def tracks_get(self, data):
        coro = [self.Track_links(isrc) for isrc in data]
        tasks = [asyncio.create_task(c) for c in coro]
        tracks = await asyncio.gather(*tasks)
        return tracks
    
    async def tracks_matcher(self, data):
        coro = [self.matcher_links(isrc) for isrc in data]
        tasks = [asyncio.create_task(c) for c in coro]
        tracks = await asyncio.gather(*tasks)
        return tracks
        
