from flask import Flask, render_template, url_for, session, redirect, request, jsonify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask_oauthlib.client import OAuth
from api_keys import *
from flask_talisman import Talisman

app = Flask(__name__)
Talisman(app, content_security_policy=None)
app.debug = False
app.secret_key = 'development'
oauth = OAuth(app)

spotipy_ = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

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
#     callback = url_for(
#         'generator',
#         _external=True
#     )
#     return spotify.authorize(callback=callback)
#
#
# @app.route('/machine', methods=['GET', 'POST'])
# def generator():
#     resp = spotify.authorized_response()
#     session['oauth_token'] = (resp['access_token'], '')

    # https://developer.spotify.com/console/get-available-genre-seeds/
    available_genres = ['acoustic', 'afrobeat', 'alt-rock', 'alternative', 'ambient', 'anime', 'black-metal',
                        'bluegrass', 'blues', 'bossanova', 'brazil', 'breakbeat', 'british', 'cantopop',
                        'chicago-house', 'children', 'chill', 'classical', 'club', 'comedy', 'country', 'dance',
                        'dancehall', 'death-metal', 'deep-house', 'detroit-techno', 'disco', 'disney', 'drum-and-bass',
                        'dub', 'dubstep', 'edm', 'electro', 'electronic', 'emo', 'folk', 'forro', 'french', 'funk',
                        'garage', 'german', 'gospel', 'goth', 'grindcore', 'groove', 'grunge', 'guitar', 'happy',
                        'hard-rock', 'hardcore', 'hardstyle', 'heavy-metal', 'hip-hop', 'holidays', 'honky-tonk',
                        'house', 'idm', 'indian', 'indie', 'indie-pop', 'industrial', 'iranian', 'j-dance', 'j-idol',
                        'j-pop', 'j-rock', 'jazz', 'k-pop', 'kids', 'latin', 'latino', 'malay', 'mandopop', 'metal',
                        'metal-misc', 'metalcore', 'minimal-techno', 'movies', 'mpb', 'new-age', 'new-release', 'opera',
                        'pagode', 'party', 'philippines-opm', 'piano', 'pop', 'pop-film', 'post-dubstep', 'power-pop',
                        'progressive-house', 'psych-rock', 'punk', 'punk-rock', 'r-n-b', 'rainy-day', 'reggae',
                        'reggaeton', 'road-trip', 'rock', 'rock-n-roll', 'rockabilly', 'romance', 'sad', 'salsa',
                        'samba', 'sertanejo', 'show-tunes', 'singer-songwriter', 'ska', 'sleep', 'songwriter', 'soul',
                        'soundtracks', 'spanish', 'study', 'summer', 'swedish', 'synth-pop', 'tango', 'techno',
                        'trance', 'trip-hop', 'turkish', 'work-out', 'world-music']

    return render_template("machine/index.html",
                           available_genres=available_genres)


@app.route("/search/<string:box>")
def process(box):

    search_limit = 10

    if box == 'artist_names':
        artists = []
        name = request.args.get('query')
        results = spotipy_.search(q='artist:' + name, type='artist', limit=search_limit)
        items = results['artists']['items']
        for i in range(len(items)):
            artist = items[i]
            # do not rename keys' names! 'value' and 'data' must remain
            # otherwise autosuggestion field does not work
            artists.append({'value': str(artist['name']), 'data': str(artist['id'])})
        # suggestions should look as follows:
        # suggestions = [{'value': 'artist1','data': '123'}, {'value': 'artist2','data': '456'}]
        suggestions = artists
    if box == 'songs':
        tracks = []
        name = request.args.get('query')
        results = spotipy_.search(q='track:' + name, type='track', limit=search_limit)
        items = results['tracks']['items']
        for i in range(len(items)):
            track = items[i]
            tracks.append({'value': str(track['name'])+" - "+str(track['artists'][0]['name']), 'data': str(track['id'])})
        suggestions = tracks

    return jsonify({"suggestions": suggestions})


@app.route('/preview', methods=['GET', 'POST'])
def preview():
    playlist_ids = []
    playlist_tracks = []
    playlist_artists = []

    recommendations = spotipy_.recommendations(seed_artists=[request.form['seed_artists']],
                                               seed_genres=[request.form['seed_genres']],
                                               seed_tracks=[request.form['seed_tracks']],
                                               target_danceability=request.form['danceability'],
                                               target_instrumentalness=request.form['instrumentalness'],
                                               target_energy=request.form['energy'],
                                               target_valence=request.form['valence'],
                                               limit=10)

    for i in range(len(recommendations['tracks'])):
        playlist_ids.append(recommendations['tracks'][i]['uri'])
        playlist_tracks.append(recommendations['tracks'][i]['name'])
        playlist_artists.append(recommendations['tracks'][i]['artists'][0]['name'])

    return render_template("preview/index.html",
                           playlist_ids=playlist_ids,
                           playlist_tracks=playlist_tracks,
                           playlist_artists=playlist_artists,
                           suggestion = request.args.get('suggestion'))

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


@app.route('/about')
def about():
    return render_template("about/index.html")


@spotify.tokengetter
def get_spotify_oauth_token():
    return session.get('oauth_token')


if __name__ == '__main__':
    app.run()
