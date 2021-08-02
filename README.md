# Playlist Machine



This is a tool that lets you generate Spotify playlists based on ("inspired by") a specified artist and song. You can also choose a genre and set up audio features.

Live app: https://playlistmachine.herokuapp.com/

![screenshot](./static/assets/images/screenshot.png)

### Running locally

1. Create a developer account in Spotify -> https://developer.spotify.com/

2. There you can obtain your API credentials: *client_id* and *client_secret*.

3. In a root directory of the project, create a file `api_keys.py` with a following content:

   ```python
   client_id = "your client id"
   client_secret = "your client secret"
   ```



