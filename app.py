from flask import Flask, render_template, url_for, session, redirect, request
from flask_oauthlib.client import OAuth
from functions import artist_name_to_id, track_name_to_id
from api_keys import *
import json

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

spotify = oauth.remote_app(
    'spotify',
    consumer_key=SPOTIFY_APP_ID,
    consumer_secret=SPOTIFY_APP_SECRET,
    request_token_params={'scope': 'playlist-modify-public playlist-modify-private user-read-private'},
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


    playlist_ids = []
    playlist_tracks = []
    playlist_artists = []

    recommendations = spotify.get('https://api.spotify.com/v1/recommendations',
                                  data={'seed_artists': artist_name_to_id(request.form['seed_artists']),
                                        'seed_tracks': track_name_to_id(request.form['seed_tracks']),
                                        'seed_genres': request.form['seed_genres'],
                                        'target_danceability': request.form['danceability'],
                                        'target_instrumentalness': request.form['instrumentalness'],
                                        'target_energy': request.form['energy'],
                                        'target_valence': request.form['valence'],
                                        'limit': '10'
                                        })

    for i in range(len(recommendations.data['tracks'])):
        playlist_ids.append(recommendations.data['tracks'][i]['uri'])
        playlist_tracks.append(recommendations.data['tracks'][i]['name'])
        playlist_artists.append(recommendations.data['tracks'][i]['artists'][0]['name'])

    return render_template("preview/index.html",
                           playlist_ids=playlist_ids,
                           playlist_tracks=playlist_tracks,
                           playlist_artists=playlist_artists)


@app.route('/saved', methods=['GET', 'POST'])
def save_playlist(name="playlist_name"):
    name = request.form['playlist_name']
    user = spotify.get('https://api.spotify.com/v1/me')
    user_id = user.data['id']

    # create playlist
    create_playlist = spotify.post('https://api.spotify.com/v1/users/' + user_id + '/playlists',
                        data={'name': name, 'description': 'a playlist created with Playlist Machine'}, format='json')
    playlist_id = create_playlist.data['id']

    # add songs to a playlist
    url = 'https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks'
    list_of_tracks = request.form.getlist('list_of_tracks')
    data = {"uris": list_of_tracks}
    spotify.post(url=url, data=data, format='json')

    return render_template("saved/index.html", playlist_id = playlist_id)

@spotify.tokengetter
def get_spotify_oauth_token():
    return session.get('oauth_token')


if __name__ == '__main__':
    app.run()
