import json
import os
from pathlib import Path

from ytmusicapi import YTMusic, OAuthCredentials

class YtMusicController:
    def __init__(self):
        self.oauth_path = Path(__file__).resolve().parent.parent / 'oauth.json'
        self.yt_music = YTMusic(
            str(self.oauth_path),
            oauth_credentials=OAuthCredentials(
                client_id=os.getenv("YOUTUBE_CLIENT_ID") or str(),
                client_secret=os.getenv("YOUTUBE_CLIENT_ID") or str()
            )
        )

    def create_playlist(self, song_ids_to_add, playlist_name, playlist_description, playlist_privacy="PRIVATE"):
        try:
            if len(song_ids_to_add) > 0:
                playlist_id = self.yt_music.create_playlist(playlist_name, playlist_description, playlist_privacy, song_ids_to_add)

                if not isinstance(playlist_id, str):
                    raise Exception(f"{self.create_playlist.__name__} Creating a playlist failed with error: {playlist_id}")
        except Exception as e:
            print(f'{self.create_playlist.__name__} failed: {e}')

    def update_playlist(self, playlist_id):
        try:
            existing_video_ids = self._get_video_ids_from_playlists(playlist_id)
            all_tracks = self._get_yt_video_ids(existing_video_ids)

            for track_id in all_tracks:
                if track_id not in existing_video_ids:
                    # TODO Update playlist, current ytmusicapi.add_playlist_items is broken so wip
                    print(f'{self.update_playlist.__name__} Add trackId {track_id} to playlist')

        except Exception as e:
            print(f'{self.update_playlist.__name__} YtMusicController.update_playlist failed: {e}')

    def _get_yt_video_ids(self, existing_ids=None):
        try:
            with Path('./Data/DataFromSpotify.json').open('r') as file:
                songs = json.load(file)

            song_ids_to_add_to_playlist = []
            for song_key in songs:
                song = songs[song_key]
                song_title = song['title']
                song_artist = song['artist']

                try:
                    search_results = self.yt_music.search(f"{song_title} {song_artist}", filter="songs", limit=3)
                    if search_results is None:
                        print(f'{self._get_yt_video_ids.__name__} Could not find a videoId for {song_title} {song_artist}')

                    if existing_ids is None or (existing_ids and search_results[0]['videoId'] not in existing_ids):
                        song_ids_to_add_to_playlist.append(search_results[0]['videoId'])
                except Exception as e:
                    print(f'{self._get_yt_video_ids.__name__} Error occured when finding videoId for {song_title} {song_artist}: {e}')

            return song_ids_to_add_to_playlist

        except Exception as e:
            print(f'{self._get_yt_video_ids.__name__} failed: {e}')
            return []

    def _get_video_ids_from_playlists(self, playlist_id):
        try:
            response = self.yt_music.get_playlist(playlist_id)
            video_ids = {video_id for video_id in response['tracks']['videoId']}

            return video_ids
        except Exception as e:
            print(f'{self._get_video_ids_from_playlists.__name__} failed: {e}')
