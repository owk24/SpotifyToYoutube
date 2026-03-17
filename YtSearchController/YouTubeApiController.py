import json
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path

import asyncio
import yt_dlp
from mutagen.mp3 import MP3

from YtSearchController.Helpers import Helpers

class YouTubeApiController:
    specialCharactersToRemove = ['/', '\\']
    smallThreshold = 3/120
    mediumThreshold = 6/120
    path = './music'
    archiveFolderPath = 'Archives'

    async def get_youtube_links_from_songs(self):
        try:
            with Path('./Data/DataFromSpotify.json').open('r') as file:
                songs = json.load(file)
            with Path('./Data/SongsWithUrls.json').open('r') as file:
                songsWithUrls = json.load(file)

            for songKey in songs:
                song = songs[songKey]
                songDuration = song['durationMs'] / 60000
                songTitle = song['title']
                songAlbum = song['album']
                songArtist = song['artist']

                if ('url' in song or songKey in songsWithUrls):
                    continue

                searchRequest = f"{songTitle} {songArtist} official audio"
                searchResultJsons = Helpers().GetYtSearchResults(searchRequest, 3)
                ytLink = self.find_matching_yt_link(searchResultJsons, songDuration, songTitle)
                song['url'] = ytLink
                songsWithUrls[songKey] = song

                if (ytLink != None):
                    continue

                searchRequest = f"{songTitle} {songAlbum} {songArtist} lyrics"
                searchResultJsons = Helpers().GetYtSearchResults(searchRequest, 20)
                ytLink = self.find_matching_yt_link(searchResultJsons, songDuration, songTitle)
                song['url'] = ytLink
                songsWithUrls[songKey] = song
            
            with Path('./Data/SongsWithUrls.json').open('w') as fp:
                json.dump(songsWithUrls, fp, indent=4)
            
            print(f'{self.get_youtube_links_from_songs.__name__} success')
        except Exception as e:
            print(f'{self.get_youtube_links_from_songs.__name__} failed due to exception: {e}')

    def find_matching_yt_link(self, searchResults, songDuration, songTitle):
        for searchResult in searchResults['videos']:
            ytSongTitle = searchResult['title']
            isSongInCorrectLocale = Helpers().SongIsCorrectLocale(songTitle, ytSongTitle)
            if isSongInCorrectLocale and Helpers().IsSongDurationWithinThreshold(songDuration, self.smallThreshold, searchResult['duration']):
                return Helpers().GetCompleteYtUrl(searchResult)
        
        return None

    async def download_songs(self):
        try:
            currentlyDownloadedSongs = self.get_current_downloaded_songs()

            failedDownLoads = {}
            with Path('./Data/SongsWithUrls.json').open('r') as file:
                songs = json.load(file)
            
            for key in songs:
                song = songs[key]
                title = song['title']
                artist = song['artist']
                album = song['album']

                if len(currentlyDownloadedSongs) > 0 and key in currentlyDownloadedSongs: # type: ignore
                    print(f'{self.download_songs.__name__} Skipped downloading {title} {artist}')
                    continue

                if ('url' not in song):
                    failedDownLoads[key] = song
                    print(f'{self.download_songs.__name__} Error downloading {title} {artist} due to no url')
                    continue

                url = song['url']

                for c in self.specialCharactersToRemove:
                    title = title.replace(c, "")
                    artist = artist.replace(c, "")
                path = join(path, f'{title}_{artist}.%(ext)s')
                try:
                    with yt_dlp.YoutubeDL(self.create_yt_dlp_options(title, artist, album, key, path, False, True)) as ydl:
                        print(f'{self.download_songs.__name__} Downloading {title} {artist} ...')
                        ydl.download(url)
                        print(f'{self.download_songs.__name__} Successfully downloaded {title} {artist}')
                except Exception as e:
                    failedDownLoads[key] = song
                    print(f'Error downloading {title} {artist} due to {e}')

            if failedDownLoads:
                with Path('./Data/Failed.json').open('r') as fp:
                    json.dump(failedDownLoads, fp, indent=4)
                print(f'{self.download_songs.__name__} Failed downloading all songs. {len(failedDownLoads)} songs failed to download.')
        except Exception as e:
            print(f'{self.download_songs.__name__} failed due to exception: {e}')

    
    async def download_from_yt_playlist(self, playlistId):
        try:
            playlistUrl = Helpers().GetYtPlaylistUrl(playlistId)
            print(f'{self.download_from_yt_playlist.__name__} starting download from playlist {playlistUrl}')
            with yt_dlp.YoutubeDL(self.create_yt_dlp_options(path='./Music', setThumbnail=True, playlistId=playlistId)) as ydl:
                ydl.download([playlistUrl])

            print(f'{self.download_from_yt_playlist.__name__} success')
        except Exception as e:
            print(f'{self.download_from_yt_playlist.__name__} failed: {e}')
    
    def get_current_downloaded_songs(self):
        currentlyDownloadedSongs = {}
        try:
            files = [f for f in listdir(self.path) if isfile(join(self.path, f))]

            if files:
                for songFile in files:
                    if songFile.endswith(".mp3"):
                        audio = MP3(self.path + f'/{songFile}')

                        if not audio:
                            continue

                        if 'Industry' in audio.tags['TIT2'].text[0]:
                            print(audio)

                        info = {
                            "title": audio.tags['TIT2'].text[0],
                            "artist": audio.tags['TPE1'].text[0],
                            "album": audio.tags['TALB'].text[0],
                            "description": audio.tags['TXXX:description'].text[0],
                            "duration": audio.info.length,  # seconds
                        }

                        currentlyDownloadedSongs[info['description']] = info['title']
            
            return currentlyDownloadedSongs
        except:
            print(f'{self.get_current_downloaded_songs.__name__} Could not access downloaded files')
    
    def create_yt_dlp_options(self, title='', artist='', album='', key='', path = '', playlistId = '', setThumbnail=False, manuallySetMetaData=False):
        archivePath = join(self.archiveFolderPath, 'archive.txt' if playlistId == '' else f'{playlistId}.txt')
        os.makedirs(os.path.dirname(archivePath), exist_ok=True)  # ensure folder exists

        options = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s_%(album)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'ignoreerrors': 'only_download',
            'skip_unavailable_fragments': True,
            'download_archive': archivePath,
            'outtmpl': join(path, f'%(title)s_%(album)s.%(ext)s'),
            'ffmpeg_location': r'C:\ffmpeg\bin',
            'writethumbnail': True,
            'convert_thumbnails': 'jpg',
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'm4a',
                    'preferredquality': '192',
                }
            ],
            'retries': 3,
            # Interval of 5 - 10 seconds between each download to prevent rate-limiting
            'sleep_interval': 5,
            'max_sleep_interval': 10,
        }

        if manuallySetMetaData:
            options['postprocessor_args'] = (
                { 
                    'FFmpegMetadata': [
                        '-metadata', f'title={title}',
                        '-metadata', f'artist={artist}',
                        '-metadata', f'album={album}',
                        '-metadata', f'description={key}',
                    ]
                }
            )
        else:
            options['postprocessors'].extend([
                {
                    'key': 'FFmpegMetadata',
                    'add_metadata': True
                }
            ])

        if setThumbnail:
            postProcessorArg = {
                'thumbnailsconvertor+ffmpeg_o': [
                    '-c:v', 'mjpeg',
                    '-qmin', '1',
                    '-qscale:v', '1',
                    '-vf', "crop='min(iw,ih)':'min(iw,ih)'"
                ]
            }

            options['postprocessors'].extend([
                {
                    # must be before EmbedThumbnail
                    'key': 'FFmpegThumbnailsConvertor',
                    'format': 'jpg'
                },
                {
                    'key': 'EmbedThumbnail',
                }
            ])

            if hasattr(options, 'postprocessor_args'):
                options['postprocessor_args'].update(postProcessorArg)
            else:
                options['postprocessor_args'] = postProcessorArg
            
        return options
