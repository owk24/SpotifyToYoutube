import json
from pathlib import Path

from ytmusicapi import YTMusic

class YtMusicController:
    ytMusic = YTMusic('./browser.json')

    def create_playlist(self, songIdsToAdd, playlistName, playlistDescription, playlistPrivacy = "PRIVATE"):
        try:
            if len(songIdsToAdd) > 0:
                playlistId = self.ytMusic.create_playlist(playlistName, playlistDescription, playlistPrivacy, songIdsToAdd)

                if not isinstance(playlistId, str):
                    raise Exception(f"{self.create_playlist.__name__} Creating a playlist failed with error: {playlistId}")
                
        except Exception as e:
            print(f'{self.create_playlist.__name__}  failed: {e}')
    
    def update_playlist(self, playlistId):
        try:
            existingVideoIds = self.get_videoIds_from_playlists(playlistId)
            allTracks = self.get_yt_video_ids(existingVideoIds)

            for trackId in allTracks:
                if trackId not in existingVideoIds:
                    # TODO Update playlist, current ytmusicapi.add_playlist_items is broken so wip
                    print(f'{self.update_playlist.__name__} Add trackId {trackId} to playlist')

        except Exception as e:
            print(f'{self.update_playlist.__name__} YtMusicController.UpdatePlaylist failed: {e}')
    
    def get_yt_video_ids(self, existingIds=None):
        try:
            with Path('./Data/DataFromSpotify.json').open('r') as file:
                songs = json.load(file)
            songIdsToAddToPlaylist = []
            for songKey in songs:
                song = songs[songKey]
                songTitle = song['title']
                songArtist = song['artist']
                
                try:
                    searchResults = self.ytMusic.search(f"{songTitle} {songArtist}", filter="songs", limit=3)
                    if searchResults == None:
                        print(f'{self.get_yt_video_ids.__name__} Could not find a videoId for {songTitle} {songArtist}')

                    if existingIds == None or (existingIds and searchResults[0]['videoId'] not in existingIds):
                        songIdsToAddToPlaylist.append(searchResults[0]['videoId'])
                # TODO not have nested try excepts
                except Exception as e:
                    print(f'{self.get_yt_video_ids.__name__} Error occured when finding videoId for {songTitle} {songArtist}: {e}')
                    
            return songIdsToAddToPlaylist

        except Exception as e:
            print(f'{self.get_yt_video_ids.__name__} failed: {e}')
            return []

    def get_videoIds_from_playlists(self, playlistId):
        try:
            response = self.ytMusic.get_playlist(playlistId)
            videoIds = {videoId for videoId in response['tracks']['videoId']}

            return videoIds
        except Exception as e:
            print(f'{self.get_videoIds_from_playlists.__name__} failed: {e}')
