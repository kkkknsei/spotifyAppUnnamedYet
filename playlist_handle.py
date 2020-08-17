import spotipy
from spotipy.oauth2 import SpotifyOAuth
import info

# As you can see here, I'm using a library called "spotipy" it's on "Spotify for Developers" documentation. I only
# started working with it as I started this file and helped a lot, you can see it on the size of the file but also on
# the structure.
# This one will only handle the playlist creation and filling it with the tracks.


class Process:
    # Authenticating the user. It'll redirect you to the auth page, make sure you're logged with the same account you
    # filled on 'info.username'

    def __init__(self):
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(client_id=info.client_id, client_secret=info.client_secret,
                                      redirect_uri=info.redirect,
                                      scope=info.scope, cache_path=info.CACHE, username=info.username,
                                      show_dialog=True))

    # Creating the playlist and returning the id of it. We'll need it later.
    def create_playlist(self):
        results = self.sp.user_playlist_create(user=info.username,
                                               public=False,
                                               description=info.playlist_desc,
                                               name=info.playlist_name)

        playlist_id = (str(results["uri"])).split("spotify:playlist:")[1]
        self.playlist_id_store = playlist_id
        return playlist_id

    # Adding each track on the tracks.txt temp file
    def add_tracks(self):
        tracks = []
        store = []
        with open("tracks.txt", "r") as linksfile:
            for row in linksfile:
                current_track_id = row.split("https://open.spotify.com/track/")[1][:-1]
                tracks.append(len(tracks) + 1)
                tracks[len(tracks) - 1] = current_track_id
            for i in range(len(tracks)):
                store.append(tracks[i])
                # So, here's the ting: you can pass an array of ids as an argument but it'll only accept 100 tracks
                # at time, so I took care of it with an "store" array an iterate
                if len(store) == 100:
                    self.sp.user_playlist_add_tracks(info.client_id, playlist_id=self.playlist_id_store, tracks=store)
                    store = []
                elif i == len(tracks) - 1:
                    self.sp.user_playlist_add_tracks(info.client_id, playlist_id=self.playlist_id_store, tracks=store)

    # Print the collected results, including the playlist_name and link
    def print_results(self):
        playlist_id = self.playlist_id_store
        print(f'Playlist Name: {info.playlist_name}')
        print(f'Playlist link: https://open.spotify.com/playlist/{playlist_id}')


# Initiating the process
if __name__ == "__main__":
    pros = Process()
    pros.create_playlist()
    pros.add_tracks()
    pros.print_results()

# TAKE A LOOK AT THE "info.py" FILE!
