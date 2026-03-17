import json
import os
from pathlib import Path

import spotipy
import spotipy.util as util

from . import SpotifyConstants

class SpotifyApiController:
    clientId = os.getenv("SPOTIFY_CLIENT_ID")
    clientSecret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirectUri = SpotifyConstants.REDIRECT_URI
    mainSearchUrl = SpotifyConstants.MAIN_SEARCH_URI
    parameterType = SpotifyConstants.PARAMETER_TYPE
    limit = SpotifyConstants.LIMIT

    scope = os.getenv("SPOTIFY_SCOPE")
    username = os.getenv("SPOTIFY_USERNAME")

    token = util.prompt_for_user_token(
        username,
        scope,
        client_id=clientId,
        client_secret=clientSecret,
        redirect_uri=redirectUri
    )

    def get_song_data_from_user_liked_list(self):
        try:
            sp = spotipy.Spotify(auth=self.token)

            tracksToProcess = sp.current_user_saved_tracks()
            if tracksToProcess == None:
                raise Exception(f'{self.get_song_data_from_user_liked_list.__name__} No songs could be found in user\'s Liked List')
            songs = {}
            while tracksToProcess:
                for item in tracksToProcess['items']:
                    song = {}

                    trackName = item['track']['name']
                    album = item['track']['album']['name']
                    artistName = item['track']['artists'][0]['name']
                    duration = item['track']['duration_ms']
                    songId = item['track']['id']

                    key = f'{trackName.strip()}_{artistName.strip()}_{songId}'

                    song['title'] = trackName
                    song['album'] = album
                    song['artist'] = artistName
                    song['durationMs'] = duration
                    song['spotifySongId'] = songId

                    songs[key] = song
                
                if tracksToProcess['next'] is not None:
                    tracksToProcess = sp.next(tracksToProcess)
                else:
                    break

            with Path('./Data/DataFromSpotify.json').open('w') as fp:
                json.dump(songs, fp, indent=4)

            print(f'{self.get_song_data_from_user_liked_list.__name__} success')
        except Exception as e:
            print(f'{self.get_song_data_from_user_liked_list.__name__} failed due to exception: {e}')