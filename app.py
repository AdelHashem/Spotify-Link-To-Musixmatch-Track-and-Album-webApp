from flask import Flask, request, render_template
from asgiref.wsgi import WsgiToAsgi
from mxm import MXM
from spotify import Spotify
import re
import aiohttp

class StartAiohttp:
    session = None
    def __init__(self,limit, limit_per_host) -> None:
        self.limit = limit
        self.limit_per_host = limit_per_host
        

    def start_session(self):
        connector = aiohttp.TCPConnector(limit=self.limit, limit_per_host=self.limit_per_host)
        self.session = aiohttp.ClientSession(connector=connector)

    def get_session(self):
        return self.session


    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

client = StartAiohttp(5,5)


app = Flask(__name__)
sp = Spotify()

@app.route('/', methods=['GET'])
async def index():
    link = request.args.get('link')
    if link:
        client.start_session()
        mxm = MXM("1a5c1f4609e375a9784e88cb42fd084f",session=client.get_session())
        try:
            if(len(link) < 12): return render_template('index.html', tracks_data= ["Wrong Spotify Link Or Wrong ISRC"])
            elif re.search(r'artist/(\w+)', link): return render_template('index.html',artist=sp.artist_albums(link,[]))
            else: sp_data = sp.get_isrc(link) if len(link) > 12 else [{"isrc": link, "image": None}]
        except Exception as e:
            return render_template('index.html', tracks_data= [str(e)])
            
        mxmLinks = await mxm.Tracks_Data(sp_data)
        if isinstance(mxmLinks, str):
            return mxmLinks
        
        await client.close_session()

        return render_template('index.html', tracks_data= mxmLinks)

    return render_template('index.html')

asgi_app = WsgiToAsgi(app)
if __name__ == '__main__':
    import asyncio
    from hypercorn.config import Config
    from hypercorn.asyncio import serve
    asyncio.run(serve(app, Config()))
    #app.run(debug=True)