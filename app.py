from flask import Flask, render_template, url_for, session, redirect, request
from flask_oauthlib.client import OAuth
from functions import artist_name_to_id, track_name_to_id
from api_keys import *

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

spotify = oauth.remote_app(
    'spotify',
    consumer_key=SPOTIFY_APP_ID,
    consumer_secret=SPOTIFY_APP_SECRET,
    request_token_params={'scope': 'playlist-modify-public'},
    base_url='https://accounts.spotify.com',
    request_token_url=None,
    access_token_url='/api/token',
    authorize_url='https://accounts.spotify.com/authorize'
)


@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect(url_for('login'))


@app.route('/login')
def login():
    callback = url_for(
        'generator',
        _external=True
    )
    return spotify.authorize(callback=callback)


@app.route('/machine', methods=['GET', 'POST'])
def generator():
    resp = spotify.authorized_response()
    session['oauth_token'] = (resp['access_token'], '')

    return render_template("machine/index.html")


@app.route('/preview', methods=['GET', 'POST'])
def preview():

    playlist = []
    playlist_preview = []

    recommendations = spotify.get('https://api.spotify.com/v1/recommendations',
                                  data={'seed_artists': artist_name_to_id(request.form['seed_artists']),
                                        'seed_tracks': track_name_to_id(request.form['seed_tracks']),
                                        'seed_genres': request.form['seed_genres'],
                                        'target_danceability': request.form['danceability'],
                                        'target_instrumentalness': request.form['instrumentalness'],
                                        'target_energy': request.form['energy'],
                                        'target_valence': request.form['valence']
                                        })

    for i in range(len(recommendations.data['tracks'])):
        playlist.append(recommendations.data['tracks'][i]['uri'])
        playlist_preview.append(recommendations.data['tracks'][i]['name'] + " - " +
                                recommendations.data['tracks'][i]['artists'][0]['name'])

    return render_template("preview/index.html",
                           playlist_preview=playlist_preview,
                           playlist=playlist)


@app.route('/saved', methods=['GET', 'POST'])
def save_playlist():
    return render_template("saved/index.html")


@spotify.tokengetter
def get_spotify_oauth_token():
    return session.get('oauth_token')


if __name__ == '__main__':
    app.run()
