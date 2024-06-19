import re
import json
import datetime
import base64
import hmac
import hashlib
import os
import aiohttp
from flask import Flask, request, render_template, make_response
from asgiref.wsgi import WsgiToAsgi
from mxm import MXM
from spotify import Spotify


secret_key_value = os.environ.get("secret_key")

SECRET_KEY = secret_key_value

SECRET_KEY = SECRET_KEY.encode('utf-8')


def generate_token(payload):
    header = {'alg': 'HS256', 'typ': 'JWT'}
    encoded_header = base64.urlsafe_b64encode(
        json.dumps(header).encode('utf-8')).rstrip(b'=')
    encoded_payload = base64.urlsafe_b64encode(
        json.dumps(payload).encode('utf-8')).rstrip(b'=')

    signature = hmac.new(SECRET_KEY, encoded_header +
                         b'.' + encoded_payload, hashlib.sha256).digest()
    encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b'=')

    return encoded_header + b'.' + encoded_payload + b'.' + encoded_signature


def verify_token(token):
    encoded_header, encoded_payload, encoded_signature = token.split('.')

    header = base64.urlsafe_b64decode(encoded_header + '==').decode('utf-8')
    payload = base64.urlsafe_b64decode(encoded_payload + '==').decode('utf-8')

    expected_signature = hmac.new(
        SECRET_KEY, (encoded_header + '.' + encoded_payload).encode('utf-8'), hashlib.sha256).digest()
    expected_encoded_signature = base64.urlsafe_b64encode(
        expected_signature).rstrip(b'=')

    if expected_encoded_signature != encoded_signature.encode('utf-8'):
        return False

    payload = json.loads(payload)
    return payload

def jwt_ref(resp,payload):
    current_time = datetime.datetime.now()
    payload["exp"] = int(
        (current_time + datetime.timedelta(days=3)).timestamp())
    new_token = generate_token(payload)
    expire_date = current_time + datetime.timedelta(days=3)
    resp.set_cookie("api_token", new_token.decode('utf-8'), expires=expire_date)
    return resp


class StartAiohttp:
    session = None

    def __init__(self, limit, limit_per_host) -> None:
        self.limit = limit
        self.limit_per_host = limit_per_host

    def start_session(self):
        self.close_session()
        connector = aiohttp.TCPConnector(
            limit=self.limit, limit_per_host=self.limit_per_host)
        self.session = aiohttp.ClientSession(connector=connector)

    def get_session(self):
        return self.session

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None


client = StartAiohttp(7, 7)


app = Flask(__name__)
sp = Spotify()


@app.route('/', methods=['GET'])
async def index():
    if request.cookies.get('api_key'):
        payload = {"mxm-key": request.cookies.get('api_key'), "exp": int(
            (datetime.datetime.now() + datetime.timedelta(days=3)).timestamp())}
        token = generate_token(payload)

        resp = make_response(render_template(
            "index.html"))
        expire_date = datetime.datetime.now() + datetime.timedelta(hours=1)
        resp.delete_cookie("api_key")
        resp.set_cookie("api_token", token, expires=expire_date)
        return resp


    link = request.args.get('link')
    key = None
    token = request.cookies.get('api_token')
    if link:
        if token:
            payload = verify_token(token)
            if payload:
                key = payload.get("mxm-key")

        client.start_session()
        mxm = MXM(key, session=client.get_session())
        try:
            if (len(link) < 12):
                return render_template('index.html', tracks_data=["Wrong Spotify Link Or Wrong ISRC"])
            elif re.search(r'artist/(\w+)', link):
                return render_template('index.html', artist=sp.artist_albums(link, []))
            else:
                sp_data = sp.get_isrc(link) if len(link) > 12 else [
                    {"isrc": link, "image": None}]
        except Exception as e:
            return render_template('index.html', tracks_data=[str(e)])

        mxmLinks = await mxm.Tracks_Data(sp_data)
        if isinstance(mxmLinks, str):
            return mxmLinks

        await client.close_session()

        return render_template('index.html', tracks_data=mxmLinks)

    # refresh the token every time the user enter the site
    if token:
        payload = verify_token(token)
        resp = make_response(render_template(
            "index.html"))
        resp = jwt_ref(resp,payload)
        return resp

    return render_template('index.html')


@app.route('/split', methods=['GET'])
async def split():
    link = request.args.get('link')
    link2 = request.args.get('link2')
    key = None
    if link and link2:
        token = request.cookies.get('api_token')
        if token:
            payload = verify_token(token)
            if payload:
                key = payload.get("mxm-key")
        client.start_session()
        mxm = MXM(key, session=client.get_session())
        match = re.search(r'open.spotify.com',
                            link) and re.search(r'track', link)
        match = match and re.search(
            r'open.spotify.com', link2) and re.search(r'track', link2)
        if match:
            sp_data1 = sp.get_isrc(link)
            sp_data2 = sp.get_isrc(link2)
            track1 = await mxm.Tracks_Data(sp_data1, True)
            track1 = track1[0]
            if isinstance(track1, str):
                return render_template('split.html', error="track1: " + track1)
            track2 = await mxm.Tracks_Data(sp_data2, True)
            track2 = track2[0]
            if isinstance(track2, str):
                return render_template('split.html', error="track2: " + track1)
            await client.close_session()
            track1["track"] = sp_data1[0]["track"]
            track2["track"] = sp_data2[0]["track"]
            try:
                if track1["isrc"] != track2["isrc"] and track1["commontrack_id"] == track2["commontrack_id"]:
                    message = f"""Can be splitted </br>
                        you can c/p:</br>
                        :mxm: <a href="{track1["track_share_url"]}" target="_blank">MXM Page</a> </br>
                        :spotify: <a href="{link}" target="_blank">{track1["track"]["name"]}</a>,
                        :isrc: {track1["isrc"]} </br>
                        :spotify: <a href="{link2}" target="_blank">{track2["track"]["name"]}</a>,
                        :isrc: {track2["isrc"]}
                        """
                elif track1["isrc"] == track2["isrc"] and track1["commontrack_id"] == track2["commontrack_id"]:
                    message = "Can not be splitted as they have the Same ISRC"
                else:
                    message = "They have different Pages"
            except:
                return render_template('split.html', error="Something went wrong")

            return render_template('split.html', split_result={"track1": track1, "track2": track2}, message=message)
        else:
            return render_template('split.html', error="Wrong Spotify Link")

    else:
        return render_template('split.html')


@app.route('/spotify', methods=['GET'])
def isrc():
    link = request.args.get('link')
    if link:
        match = re.search(r'open.spotify.com', link) and re.search(
            r'track|album', link)
        if match:
            return render_template('isrc.html', tracks_data=sp.get_isrc(link))

        else:
            # the link is an isrc code
            if len(link) == 12:
                # search by isrc
                return render_template('isrc.html', tracks_data=sp.search_by_isrc(link))
            return render_template('isrc.html', tracks_data=["Wrong Spotify Link"])
    else:
        return render_template('isrc.html')


@app.route('/api', methods=['GET'])
async def setAPI():
    key = request.args.get('key')
    delete = request.args.get("delete_key")

    # Get the existing token from the cookie
    token = request.cookies.get('api_token')
    if token:
        payload = verify_token(token)
        if payload:
            key = payload.get("mxm-key")
            censored_key = '*' * len(key) if key else None

            # refresh the token each time the user enter the "/api"
            resp = make_response(render_template(
                    "api.html", key=censored_key))
            resp = jwt_ref(resp,payload)
            return resp


    if key:
        # check the key
        client.start_session()
        mxm = MXM(key, session=client.get_session())
        sp_data = [{"isrc": "DGA072332812", "image": None}]

        # Call the Tracks_Data method with the appropriate parameters
        mxmLinks = await mxm.Tracks_Data(sp_data)
        print(mxmLinks)
        await client.close_session()

        if isinstance(mxmLinks[0], str):
            return render_template("api.html", error="Please Enter A Valid Key")

        payload = {"mxm-key": key, "exp": int(
            (datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp())}
        token = generate_token(payload)

        resp = make_response(render_template(
            "api.html", key="Token Generated"))
        expire_date = datetime.datetime.now() + datetime.timedelta(hours=1)
        resp.set_cookie("api_token", token.decode('utf-8'), expires=expire_date)
        return resp

    elif delete:
        resp = make_response(render_template("api.html"))
        resp.delete_cookie("api_token")
        return resp

    else:
        return render_template("api.html", key=None)


@app.route('/mxm', methods=['GET'])
async def mxm_to_sp():
    link = request.args.get('link')
    key = None
    if link:
        token = request.cookies.get('api_token')
        if token:
            payload = verify_token(token)
            if payload:
                key = payload.get("mxm-key")

        client.start_session()
        mxm = MXM(key, session=client.get_session())
        album = await mxm.album_sp_id(link)
        await client.close_session()
        return render_template("mxm.html", album=album.get("album"), error=album.get("error"))
    else:
        return render_template("mxm.html")
    
@app.route('/abstrack', methods=['GET'])
async def abstrack() -> str:
    """ Get the track data from the abstract track """
    id = request.args.get('id')
    key = None
    if id:
        token = request.cookies.get('api_token')
        if token:
            payload = verify_token(token)
            if payload:
                key = payload.get("mxm-key")
        if not re.match("^[0-9]+$",id):
            return render_template("abstrack.html", error = "Invalid input!")
        client.start_session()
        mxm = MXM(key, session=client.get_session())
        track, album = await mxm.abstrack(id)
        await client.close_session()
        return render_template("abstrack.html", track=track, album= album, error=track.get("error"))
    else:
        return render_template("abstrack.html")


asgi_app = WsgiToAsgi(app)
if __name__ == '__main__':
    import asyncio
    from hypercorn.config import Config
    from hypercorn.asyncio import serve
    asyncio.run(serve(app, Config()))
    # app.run(debug=True)
