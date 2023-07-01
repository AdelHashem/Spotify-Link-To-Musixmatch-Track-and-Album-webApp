""" A simple Async Python library for the Musixmatch Web API """



import asyncio
import aiohttp
import json

from Asyncmxm.exceptions import MXMException

class Musixmatch(object):
    """"""

    max_retries = 3
    default_retry_codes = (429, 500, 502, 503, 504)

    def __init__(
        self,
        API_key,
        limit = 4,
        requests_session=None,
        retries=max_retries,
        requests_timeout=5,
        backoff_factor=0.3,
    ):
        """
        Create a Musixmatch Client.
        :param api_key: The API key, Get one at https://developer.musixmatch.com/signup
        :param requests_session: A Requests session object or a truthy value to create one.
        :param retries: Total number of retries to allow
        :param requests_timeout: Stop waiting for a response after a given number of seconds
        :param backoff: Factor to apply between attempts after the second try
        """

        self._url = "https://api.musixmatch.com/ws/1.1/"
        self._key = API_key
        self.requests_timeout = requests_timeout
        self.backoff_factor = backoff_factor
        self.retries = retries
        self.limit = limit 

        if isinstance(requests_session, aiohttp.ClientSession):
            self._session = requests_session
        else:
            self._build_session()

    def _build_session(self):
        connector = aiohttp.TCPConnector(limit=self.limit, limit_per_host=self.limit)
        self._session = aiohttp.ClientSession(connector=connector,loop=asyncio.get_event_loop())
    '''    
    async def __aexit__(self, exc_type, exc_value, exc_tb):
        """Make sure the connection gets closed"""
        await self._session.close()
    '''

    async def _api_call(self, method, api_method, params = None):
        url = self._url + api_method
        if params:
            params["apikey"] = self._key
        else:
            params = {"apikey": self._key}

        retries = 0

        while retries < self.max_retries:
            try:
                print(params)
                async with self._session.request(method=method, url=str(url), params = params) as response:
                    
                    response.raise_for_status()
                    res = await response.text()
                    print(res)
                    res = json.loads(res)
                    status_code = res["message"]["header"]["status_code"]
                    if status_code == 200:
                        return res
                    else:
                        retries = self.max_retries
                        hint = res["message"]["header"].get("hint") or None
                        raise MXMException(status_code,hint)
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                retries +=1
                await asyncio.sleep(self.backoff_factor * retries)
                continue
        raise Exception("API request failed after retries")
         


    async def track_get(
        self,
        commontrack_id=None,
        track_id=None,
        track_isrc=None,
        commontrack_vanity_id=None,
        track_spotify_id=None,
        track_itunes_id=None,
    ):
        """
        Get a track info from their database by objects
        Just one Parameter is required
        :param commontrack_id: Musixmatch commontrack id
        :param track_id: Musixmatch track id
        :param track_isrc: A valid ISRC identifier
        :param commontrack_vanity_id: Musixmatch vanity id ex "Imagine-Dragons/Demons"
        :param track_spotify_id: Spotify Track ID
        :param track_itunes_id: Apple track ID
        """

        params = {k: v for k, v in locals().items() if v is not None and k !='self'}
        return await self._api_call("get", "track.get", params)

    async def matcher_track_get(
        self,
        q_track=None,
        q_artist=None,
        q_album=None,
        commontrack_id=None,
        track_id=None,
        track_isrc=None,
        commontrack_vanity_id=None,
        track_spotify_id=None,
        track_itunes_id=None,
        **filters,
    ):
        """
        Match your song against Musixmatch database.

        QUERYING: (At least one required)
        :param q_track: search for a text string among song titles
        :param q_artist: search for a text string among artist names
        :param q_album: The song album

        Objects: (optional)
        :param commontrack_id: Musixmatch commontrack id
        :param track_id: Musixmatch track id
        :param track_isrc: A valid ISRC identifier
        :param commontrack_vanity_id: Musixmatch vanity id ex "Imagine-Dragons/Demons"
        :param track_spotify_id: Spotify Track ID
        :param track_itunes_id: Apple track ID

        FILTERING: (optional)
        :param f_has_lyrics: Filter by objects with available lyrics
        :param f_is_instrumental: Filter instrumental songs
        :param f_has_subtitle: Filter by objects with available subtitles (1 or 0)
        :param f_music_genre_id: Filter by objects with a specific music category
        :param f_subtitle_length: Filter subtitles by a given duration in seconds
        :param f_subtitle_length_max_deviation: Apply a deviation to a given subtitle duration (in seconds)
        :param f_lyrics_language: Filter the tracks by lyrics language
        :param f_artist_id: Filter by objects with a given Musixmatch artist_id
        :param f_artist_mbid: Filter by objects with a given musicbrainz artist id

        """

        params = {k: v for k, v in locals().items() if v is not None and k !='self' and k != "filters"}
        params = {**params, **filters}
        return await self._api_call("get", "matcher.track.get", params)

    async def chart_artists_get(self, page, page_size, country="US"):
        """
        This api provides you the list of the top artists of a given country.

        :param page: Define the page number for paginated results
        :param page_size: Define the page size for paginated results. Range is 1 to 100.
        :param country: A valid country code (default US)
        """
        params = {k: v for k, v in locals().items() if v is not None and k !='self'}
        return await self._api_call("get", "chart.artists.get", params)

    async def chart_tracks_get(
        self, chart_name,page = 1, page_size = 100, f_has_lyrics = 1, country="US"
    ):
        """
        This api provides you the list of the top artists of a given country.

        :param page: Define the page number for paginated results
        :param page_size: Define the page size for paginated results. Range is 1 to 100.
        :param chart_name: Select among available charts:
                            top : editorial chart
                            hot : Most viewed lyrics in the last 2 hours
                            mxmweekly : Most viewed lyrics in the last 7 days
                            mxmweekly_new : Most viewed lyrics in the last 7 days limited to new releases only
        :param f_has_lyrics: When set, filter only contents with lyrics, Takes (0 or 1)
        :param country: A valid country code (default US)
        """
        params = {k: v for k, v in locals().items() if v is not None and k !='self'}
        return await self._api_call("get", "chart.tracks.get", params)

    async def track_search(self, page = 1, page_size = 100, **params):
        """
        Search for track in Musixmatch database.

        :param q_track: The song title
        :param q_artist: The song artist
        :param q_lyrics: Any word in the lyrics
        :param q_track_artist: Any word in the song title or artist name
        :param q_writer: Search among writers
        :param q: Any word in the song title or artist name or lyrics
        :param f_artist_id: When set, filter by this artist id
        :param f_music_genre_id: When set, filter by this music category id
        :param f_lyrics_language: Filter by the lyrics language (en,it,..)
        :param f_has_lyrics: When set, filter only contents with lyrics
        :param f_track_release_group_first_release_date_min:
            When set, filter the tracks with release date newer than value, format is YYYYMMDD
        :param f_track_release_group_first_release_date_max:
            When set, filter the tracks with release date older than value, format is YYYYMMDD
        :param s_artist_rating: Sort by our popularity index for artists (asc|desc)
        :param s_track_rating: Sort by our popularity index for tracks (asc|desc)
        :param quorum_factor: Search only a part of the given query string.Allowed range is (0.1 - 0.9)
        :param page: Define the page number for paginated results
        :param page_size: Define the page size for paginated results. Range is 1 to 100.
        """
        locs = locals().copy()
        locs.pop("params") 
        params = {**params, **locs}
        return await self._api_call("get", "track.search", params)

    async def track_lyrics_get(self, commontrack_id=None, track_id=None, track_spotify_id=None):
        """
        Get the lyrics of a track.

        :param commontrack_id: Musixmatch commontrack id
        :param track_id: Musixmatch track id
        :param track_spotify_id: Spotify Track ID
        """
        params = {k: v for k, v in locals().items() if v is not None and k !='self'}
        return await self._api_call("get", "track.lyrics.get", params)
    
    async def track_lyrics_post(self, lyrics:str, commontrack_id=None, track_isrc=None):
        """
        Submit a lyrics to Musixmatch database.

        :param lyrics: The lyrics to be submitted
        :param commontrack_id: The track commontrack
        :param track_isrc: A valid ISRC identifier 
        """
        params = {k: v for k, v in locals().items() if v is not None and k !='self'}
        return await self._api_call("post", "track.lyrics.post", params)
    
    async def track_lyrics_mood_get(self,commontrack_id=None, track_isrc=None):
        """
        Get the mood list (and raw value that generated it) of a lyrics

        :note: Not available for the free plan

        :param commontrack_id: The track commontrack
        :param track_isrc: A valid ISRC identifier 
        """
        params = {k: v for k, v in locals().items() if v is not None and k !='self'}
        return await self._api_call("get", "track.lyrics.mood.get", params)

    async def track_snippet_get(self,commontrack_id=None, 
                          track_id=None, 
                          track_isrc=None, 
                          track_spotify_id=None
                          ):
        """
        Get the snippet for a given track.
            A lyrics snippet is a very short representation of a song lyrics. 
            It's usually twenty to a hundred characters long

        :param commontrack_id: The track commontrack
        :param track_id: Musixmatch track id
        :param track_isrc: A valid ISRC identifier
        :param track_spotify_id: Spotify Track ID
        """

        params = {k: v for k, v in locals().items() if v is not None and k !='self'}
        return await self._api_call("get", "track.snippet.get", params)
    
    async def track_subtitle_get(self,commontrack_id=None,
                           track_id=None, 
                          subtitle_format = None,
                          track_isrc=None,
                          f_subtitle_length = None,
                          f_subtitle_length_max_deviation = None
                          ):
        """
        Retreive the subtitle of a track.
        Return the subtitle of a track in LRC or DFXP format.

        :param commontrack_id: The track commontrack
        :param track_id: Musixmatch track id
        :param track_isrc: A valid ISRC identifier
        :param subtitle_format: The format of the subtitle (lrc,dfxp,stledu). Default to lrc
        :param f_subtitle_length: The desired length of the subtitle (seconds)
        :param f_subtitle_length_max_deviation: The maximum deviation allowed from the f_subtitle_length (seconds)
        """

        params = {k: v for k, v in locals().items() if v is not None and k !='self'}
        return await self._api_call("get", "track.subtitle.get", params)

    async def track_richsync_get(self,commontrack_id=None, 
                          track_id=None, 
                          track_isrc=None, 
                          track_spotify_id=None,
                          f_richsync_length = None,
                          f_richsync_length_max_deviation = None
                          ):
        """
        A rich sync is an enhanced version of the standard sync.

        :param commontrack_id: The track commontrack
        :param track_id: Musixmatch track id
        :param track_isrc: A valid ISRC identifier
        :param track_spotify_id: Spotify Track ID
        :param f_richsync_length: The desired length of the sync (seconds)
        :param f_richsync_length_max_deviation: The maximum deviation allowed from the f_sync_length (seconds)
        """

        params = {k: v for k, v in locals().items() if v is not None and k !='self'}
        return await self._api_call("get", "track.richsync.get", params)
    
    async def track_lyrics_translation_get(self,commontrack_id=None, 
                          track_id=None, 
                          track_isrc=None, 
                          track_spotify_id=None,
                          selected_language = None,
                          min_completed = None
                          ):
        """
        Get a translated lyrics for a given language

        :param commontrack_id: The track commontrack
        :param track_id: Musixmatch track id
        :param track_isrc: A valid ISRC identifier
        :param track_spotify_id: Spotify Track ID
        :param selected_language: he language of the translated lyrics (ISO 639-1)
        :param min_completed: Teal from 0 to 1. If present, 
            only the tracks with a translation ratio over this specific value, 
            for a given language, are returned Set it to 1 for completed translation only, to 0.7 for a mimimum of 70% complete translation.
        :param f_subtitle_length: The desired length of the subtitle (seconds)
        :param f_subtitle_length_max_deviation: The maximum deviation allowed from the f_subtitle_length (seconds)
        """

        params = {k: v for k, v in locals().items() if v is not None and k !='self'}
        return await self._api_call("get", "track.lyrics.translation.get", params)
    
    async def track_subtitle_translation_get(self,commontrack_id=None, 
                          track_id=None, 
                          track_isrc=None, 
                          track_spotify_id=None,
                          selected_language = None,
                          min_completed = None,
                          f_subtitle_length = None,
                          f_subtitle_length_max_deviation = None
                          ):
        """
        Get a translated subtitle for a given language

        :param commontrack_id: The track commontrack
        :param track_id: Musixmatch track id
        :param track_isrc: A valid ISRC identifier
        :param track_spotify_id: Spotify Track ID
        :param selected_language: he language of the translated lyrics (ISO 639-1)
        :param min_completed: Teal from 0 to 1. If present, 
            only the tracks with a translation ratio over this specific value, 
            for a given language, are returned Set it to 1 for completed translation only, to 0.7 for a mimimum of 70% complete translation.
        """

        params = {k: v for k, v in locals().items() if v is not None and k !='self'}
        return await self._api_call("get", "track.subtitle.translation.get", params)

    async def music_genres_get(self):
        """
        Get the list of the music genres of our catalogue.
        """
        return await self._api_call("get", "music.genres.get")
    
    async def matcher_lyrics_get(
        self,
        q_track=None,
        q_artist=None,
        q_album=None,
        commontrack_id=None,
        track_id=None,
        track_isrc=None,
        commontrack_vanity_id=None,
        track_spotify_id=None,
        track_itunes_id=None,
        **filters,
    ):
        """
        Get the lyrics for track based on title and artist

        QUERYING: (At least one required)
        :param q_track: search for a text string among song titles
        :param q_artist: search for a text string among artist names
        :param q_album: The song album

        Objects: (optional)
        :param commontrack_id: Musixmatch commontrack id
        :param track_id: Musixmatch track id
        :param track_isrc: A valid ISRC identifier
        :param commontrack_vanity_id: Musixmatch vanity id ex "Imagine-Dragons/Demons"
        :param track_spotify_id: Spotify Track ID
        :param track_itunes_id: Apple track ID

        FILTERING: (optional)
        :param f_subtitle_length: The desired length of the subtitle (seconds)
        :param f_subtitle_length_max_deviation: The maximum deviation allowed from the f_subtitle_length (seconds)
        :param f_has_lyrics: Filter by objects with available lyrics
        :param f_is_instrumental: Filter instrumental songs
        :param f_has_subtitle: Filter by objects with available subtitles (1 or 0)
        :param f_music_genre_id: Filter by objects with a specific music category
        :param f_lyrics_language: Filter the tracks by lyrics language
        :param f_artist_id: Filter by objects with a given Musixmatch artist_id
        :param f_artist_mbid: Filter by objects with a given musicbrainz artist id

        """

        params = {k: v for k, v in locals().items() if v is not None and k !='self' and k != "filters"}
        params = {**params, **filters}
        return await self._api_call("get", "matcher.lyrics.get", params)

    async def matcher_subtitle_get(
        self,
        q_track=None,
        q_artist=None,
        q_album=None,
        commontrack_id=None,
        track_id=None,
        track_isrc=None,
        commontrack_vanity_id=None,
        track_spotify_id=None,
        track_itunes_id=None,
        **filters,
    ):
        """
        Get the subtitles for a song given his title,artist and duration.
        You can use the f_subtitle_length_max_deviation to fetch subtitles within a given duration range.


        QUERYING: (At least one required)
        :param q_track: search for a text string among song titles
        :param q_artist: search for a text string among artist names
        :param q_album: The song album

        Objects: (optional)
        :param commontrack_id: Musixmatch commontrack id
        :param track_id: Musixmatch track id
        :param track_isrc: A valid ISRC identifier
        :param commontrack_vanity_id: Musixmatch vanity id ex "Imagine-Dragons/Demons"
        :param track_spotify_id: Spotify Track ID
        :param track_itunes_id: Apple track ID

        FILTERING: (optional)
        :param f_subtitle_length: The desired length of the subtitle (seconds)
        :param f_subtitle_length_max_deviation: The maximum deviation allowed from the f_subtitle_length (seconds)
        :param f_has_lyrics: Filter by objects with available lyrics
        :param f_is_instrumental: Filter instrumental songs
        :param f_has_subtitle: Filter by objects with available subtitles (1 or 0)
        :param f_music_genre_id: Filter by objects with a specific music category
        :param f_lyrics_language: Filter the tracks by lyrics language
        :param f_artist_id: Filter by objects with a given Musixmatch artist_id
        :param f_artist_mbid: Filter by objects with a given musicbrainz artist id

        """

        params = {k: v for k, v in locals().items() if v is not None and k !='self' and k != "filters"}
        params = {**params, **filters}
        return await self._api_call("get", "matcher.subtitle.get", params)

    async def artist_get(self, artist_id):
        """
        Get the artist data.

        :param artist_id: Musixmatch artist id

        """
        return await self._api_call("get", "artist.get", locals())
    
    async def artist_search(self,
                      q_artist,
                      page = 1,
                      page_size = 100,
                      f_artist_id = None                    
                      ):
        """
        Search for artists

        :param q_artist: The song artist
        :param page: Define the page number for paginated results
        :param page_size: Define the page size for paginated results. Range is 1 to 100.
        :param f_artist_id: When set, filter by this artist id
        """
        params = {k: v for k, v in locals().items() if v is not None and k !='self'}
        return await self._api_call("get", "artist.search", params)
    
    async def artist_albums_get(self,
                      artist_id,
                      page = 1,
                      page_size = 100,
                      g_album_name = 1,
                      s_release_date = "desc"
                      ):
        """
        Get the album discography of an artist

        :param q_artist: The song artist
        :param page: Define the page number for paginated results
        :param page_size: Define the page size for paginated results. Range is 1 to 100.
        :param g_album_name: Group by Album Name
        :param s_release_date: Sort by release date (asc|desc)
        """
        params = {k: v for k, v in locals().items() if v is not None and k !='self'}
        return await self._api_call("get", "artist.albums.get", params)
    
    async def artist_related_get(self,
                      artist_id,
                      page = 1,
                      page_size = 100,
                      ):
        """
        Get a list of artists somehow related to a given one.

        :param q_artist: The song artist
        :param page: Define the page number for paginated results
        :param page_size: Define the page size for paginated results. Range is 1 to 100.
        """
        params = {k: v for k, v in locals().items() if v is not None and k !='self'}
        return await self._api_call("get", "artist.related.get", params)
    
    async def album_get(self, album_id):
        """
        Get the album object using the musixmatch id.

        :param album_id: The musixmatch album id.
        """
        return await self._api_call("get", "album.get", locals())
    
    async def album_tracks_get(self, album_id,
                         f_has_lyrics = 0,
                         page = 1,
                         page_size = 100
                         ):
        """
        This api provides you the list of the songs of an album.

        :param album_id: The musixmatch album id.
        :param f_has_lyrics: When set, filter only contents with lyrics.
        :param page: Define the page number for paginated results
        :param page_size: Define the page size for paginated results. Range is 1 to 100.
        """
        return await self._api_call("get", "album.tracks.get", locals())