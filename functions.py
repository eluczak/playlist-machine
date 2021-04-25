import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from api_keys import *
spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

def artist_name_to_id(name):

    results = spotify.search(q='artist:' + name, type='artist', limit='50')
    artists = results['artists']['items']

    if len(artists) > 0:

        artists_with_same_name=[]

        for i in range(len(artists)):
            if (artists[i]['name']).lower() == name.lower():
                artist = artists[i]
                artist = [artist['id'],artist['name'],artist['popularity']]
                artists_with_same_name.append(artist)

        max=0
        for i in range(len(artists_with_same_name)):
            if artists_with_same_name[max][2] < artists_with_same_name[i][2]:
                max=i
        return(artists_with_same_name[max][0])


def track_name_to_id(name):

    # when there is more than 1 track with the same name,
    # the one with highest popularity has been returned

    spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

    track_name, artist_name = name.split('|')
    results = spotify.search(q='track:' + track_name + ' ' + 'artist:' + artist_name, type='track', limit='50')
    tracks = results['tracks']['items']

    if len(tracks) > 0:

        tracks_with_same_name=[]

        for i in range(len(tracks)):
            if tracks[i]['name'].lower() == track_name.lower() and tracks[i]['artists'][0]['name'].lower() == artist_name.lower() :
                track = tracks[i]
                track = [track['id'],track['name'],track['popularity']]
                tracks_with_same_name.append(track)

        max=0
        for i in range(len(tracks_with_same_name)):
            if tracks_with_same_name[max][2] < tracks_with_same_name[i][2]:
                max=i
        return(tracks_with_same_name[max][0])