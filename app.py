from flask import Flask, request, render_template
from mxm import MXM
from spotify import Spotify

app = Flask(__name__)
sp = Spotify()
mxm = MXM()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        link = request.form['link']
        try:
            if(len(link) < 12): return "Wrong Spotify Link Or Wrong ISRC"
            isrc = sp.get_isrc(link) if len(link) > 12 else link
        except:
            return "Wrong Spotify Link Or Wrong ISRC"
            
        mxmLinks = mxm.Track_links(isrc)
        if isinstance(mxmLinks, str):
            return mxmLinks

        return render_template('index.html', id=mxmLinks[0], isrc = isrc,track_link=mxmLinks[1].split("?")[0], album_link=mxmLinks[2])
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
