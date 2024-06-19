import os
import re
import jellyfish
import Asyncmxm 
import asyncio
from urllib.parse import unquote
import redis

class MXM:
    DEFAULT_KEY = os.environ.get("MXM_API")
    DEFAULT_KEY2 = os.environ.get("MXM_API2")

    def __init__(self, key=None, session=None):
        self.key = key or self.DEFAULT_KEY
        self.key2 = key or self.DEFAULT_KEY2 
        if not self.key:
            r = redis.Redis(
            host=os.environ.get("REDIS_HOST"),
            port=os.environ.get("REDIS_PORT"),
            password=os.environ.get("REDIS_PASSWD"))
            key1 = r.get("live:1")
            key2 = r.get("live:2")
            self.key = key1.decode()
            self.key2 = key2.decode()
            print(self.key," ", self.key2)
            r.close()


        self.session = session
        self.musixmatch = Asyncmxm.Musixmatch(self.key,requests_session=session)
        self.musixmatch2 = Asyncmxm.Musixmatch(self.key2,requests_session=session)

    def change_key(self, key):
        self.key = key

    async def track_get(self, isrc=None, commontrack_id=None, vanity_id =None) -> dict:
        try:
            response = await self.musixmatch.track_get(
                track_isrc=isrc, commontrack_id=commontrack_id,
                commontrack_vanity_id= vanity_id
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
        if isinstance(sp_data, dict):
            track = await self.track_get(sp_data.get("isrc"))
            try:
                id = track["message"]["body"]["track"]["commontrack_id"]
            except TypeError as e:
                return track

            track = track["message"]["body"]["track"]
            track["isrc"] = sp_data["isrc"]
            track["image"] = sp_data["image"]
            track["beta"] = str(track["track_share_url"]).replace("www.","com-beta.",1)
            
            return track
        else:
            return sp_data
    
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
        track["beta"] = str(track["track_share_url"]).replace("www.","beta.",1)
        return track

    async def Tracks_Data(self, sp_data, split_check = False):
        links = []
        tracks = await self.tracks_get(sp_data)


        if  isinstance(sp_data[0], dict) and sp_data[0].get("track"):
            matchers = await self.tracks_matcher(sp_data)
        else:
            return tracks

        for i in range(len(tracks)):
            track = tracks[i]
            matcher = matchers[i]
            if split_check:
                links.append(track)
                continue

            # detecting what issues can facing the track
            if isinstance(track, dict) and isinstance(matcher, dict):

                # the get call and the matcher call are the same and both have valid response
                if (track["commontrack_id"] == matcher["commontrack_id"]):
                    track["matcher_album"] = [
                        matcher["album_id"],
                        matcher["album_name"],
                    ]
                    links.append(track)
                    ''' when we get different data, the sp id attached to the matcher so we try to detect
                    if the matcher one is vailid or it just a ISRC error.
                    I used the probability here to choose the most accurate data to the spotify data
                    '''
                else: 
                    matcher_title = re.sub(r'[()-.]', '', matcher.get("track_name"))
                    matcher_album = re.sub(r'[()-.]', '', matcher.get("album_name"))
                    sp_title = re.sub(r'[()-.]', '', sp_data[i]["track"]["name"])
                    sp_album = re.sub(r'[()-.]', '', sp_data[i]["track"]["album"]["name"])
                    track_title = re.sub(r'[()-.]', '', track.get("track_name"))
                    track_album = re.sub(r'[()-.]', '', track.get("album_name"))
                    if (matcher.get("album_name") == sp_data[i]["track"]["album"]["name"]
                      and matcher.get("track_name") == sp_data[i]["track"]["name"]
                      or jellyfish.jaro_similarity(matcher_title.lower(), sp_title.lower())
                       * jellyfish.jaro_similarity(matcher_album.lower(), sp_album.lower())  >=
                         jellyfish.jaro_similarity(track_title.lower(), sp_title.lower())
                       * jellyfish.jaro_similarity(track_album.lower(), sp_album.lower()) ):
                        matcher["note"] = f'''This track may having two pages with the same ISRC,
                        the other <a class="card-link" href="{track["track_share_url"]}" target="_blank"
                        >page</a> from <a class="card-link" href="https://www.musixmatch.com/album/{(track["artist_id"])}/{(track["album_id"])}" target="_blank"
                        >album</a>.'''
                        links.append(matcher)
                    else:

                        track["note"] = f'''This track may be facing an ISRC issue
                        as the Spotify ID is connected to another <a class="card-link" href="{matcher["track_share_url"]}" target="_blank"
                        >page</a> from <a class="card-link" href="https://www.musixmatch.com/album/{(track["artist_id"])}/{(matcher["album_id"])}" target="_blank"
                        >album</a>.'''
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
                else: links.append(track)
            elif isinstance(track, str) and isinstance(matcher, dict):
                if matcher.get("album_name") == sp_data[i]["track"]["album"]["name"]:
                    links.append(matcher)
                    continue
                else: links.append(matcher)
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
    
    async def album_sp_id(self,link):
        site = re.search(r"musixmatch.com",link)
        match = re.search(r'album/([^?]+/[^?]+)|album/(\d+)|lyrics/([^?]+/[^?]+)', unquote(link))
        if match and site:
            try:
                if match.group(1):
                    album = await self.musixmatch.album_get(album_vanity_id=match.group(1))
                elif match.group(2):
                    album = await self.musixmatch.album_get(match.group(2))
                else:
                    track = await self.musixmatch.track_get(commontrack_vanity_id=match.group(3))
                    album_id = track["message"]["body"]["track"]["album_id"]
                    album = await self.musixmatch.album_get(album_id)
                print(album)
                return {"album": album["message"]["body"]["album"]}
            except Asyncmxm.exceptions.MXMException as e:
                return {"error": str(e)}
        else:
            return {"error": "Unsupported link."}

    async def abstrack(self, id : int) -> tuple[dict,dict]:
        """Get the track and the album data from the abstrack."""
        try:
            track = await self.musixmatch.track_get(commontrack_id=id)
            track = track["message"]["body"]["track"]
            album = await self.musixmatch.album_get(track["album_id"])
            album = album["message"]["body"]["album"]
            return track, album
        except Asyncmxm.exceptions.MXMException as e:
            return {"error": str(e)}, {"error": str(e)}
           
