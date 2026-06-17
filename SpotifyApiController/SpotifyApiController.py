import json
import os
from pathlib import Path

import spotipy
import spotipy.util as util

from . import SpotifyConstants

class SpotifyApiController:
    def __init__(self):
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = SpotifyConstants.REDIRECT_URI
        self.main_search_url = SpotifyConstants.MAIN_SEARCH_URI
        self.parameter_type = SpotifyConstants.PARAMETER_TYPE
        self.limit = SpotifyConstants.LIMIT

        self.scope = os.getenv("SPOTIFY_SCOPE")
        self.username = os.getenv("SPOTIFY_USERNAME")

        self.token = util.prompt_for_user_token(
            self.username,
            self.scope,
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri
        )

    def get_song_data_from_user_liked_list(self):
        try:
            spotify_client = spotipy.Spotify(auth=self.token)

            tracks_to_process = spotify_client.current_user_saved_tracks()
            if tracks_to_process is None:
                raise Exception(f'{self.get_song_data_from_user_liked_list.__name__} No songs could be found in user\'s Liked List')

            songs = {}
            while tracks_to_process:
                for item in tracks_to_process['items']:
                    song = {}

                    track_name = item['track']['name']
                    album = item['track']['album']['name']
                    artist_name = item['track']['artists'][0]['name']
                    duration = item['track']['duration_ms']
                    song_id = item['track']['id']

                    key = f'{track_name.strip()}_{artist_name.strip()}_{song_id}'

                    song['title'] = track_name
                    song['album'] = album
                    song['artist'] = artist_name
                    song['durationMs'] = duration
                    song['spotifySongId'] = song_id

                    songs[key] = song

                if tracks_to_process['next'] is not None:
                    tracks_to_process = spotify_client.next(tracks_to_process)
                else:
                    break

            with Path('./Data/DataFromSpotify.json').open('w') as fp:
                json.dump(songs, fp, indent=4)

            print(f'{self.get_song_data_from_user_liked_list.__name__} success')
        except Exception as e:
            print(f'{self.get_song_data_from_user_liked_list.__name__} failed due to exception: {e}')