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
    def __init__(self):
        self.special_characters_to_remove = ['/', '\\']
        self.small_threshold = 3/120
        self.medium_threshold = 6/120
        self.base_folder = Path(__file__).resolve().parent
        self.music_path = self.base_folder / 'Music'
        self.archive_folder_path = self.base_folder / 'Archives'
        self.helpers = Helpers()

    async def get_youtube_links_from_songs(self):
        try:
            with Path('./Data/DataFromSpotify.json').open('r') as file:
                songs = json.load(file)
            with Path('./Data/SongsWithUrls.json').open('r') as file:
                songs_with_urls = json.load(file)

            for song_key in songs:
                song = songs[song_key]
                song_duration = song['durationMs'] / 60000
                song_title = song['title']
                song_album = song['album']
                song_artist = song['artist']

                if 'url' in song or song_key in songs_with_urls:
                    continue

                search_request = f"{song_title} {song_artist} official audio"
                search_result_jsons = self.helpers.get_yt_search_results(search_request, 3)
                yt_link = self._find_matching_yt_link(search_result_jsons, song_duration, song_title)
                song['url'] = yt_link
                songs_with_urls[song_key] = song

                if yt_link is not None:
                    continue

                search_request = f"{song_title} {song_album} {song_artist} lyrics"
                search_result_jsons = self.helpers.get_yt_search_results(search_request, 20)
                yt_link = self._find_matching_yt_link(search_result_jsons, song_duration, song_title)
                song['url'] = yt_link
                songs_with_urls[song_key] = song

            with Path('./Data/SongsWithUrls.json').open('w') as fp:
                json.dump(songs_with_urls, fp, indent=4)

            print(f'{self.get_youtube_links_from_songs.__name__} success')
        except Exception as e:
            print(f'{self.get_youtube_links_from_songs.__name__} failed due to exception: {e}')

    async def download_songs(self):
        try:
            currently_downloaded_songs = self._get_current_downloaded_songs()

            failed_downloads = {}
            with Path('./Data/SongsWithUrls.json').open('r') as file:
                songs = json.load(file)

            for key in songs:
                song = songs[key]
                title = song['title']
                artist = song['artist']
                album = song['album']

                if len(currently_downloaded_songs) > 0 and key in currently_downloaded_songs:  # type: ignore
                    print(f'{self.download_songs.__name__} Skipped downloading {title} {artist}')
                    continue

                if 'url' not in song:
                    failed_downloads[key] = song
                    print(f'{self.download_songs.__name__} Error downloading {title} {artist} due to no url')
                    continue

                url = song['url']

                for c in self.special_characters_to_remove:
                    title = title.replace(c, "")
                    artist = artist.replace(c, "")
                self.music_path.mkdir(parents=True, exist_ok=True)
                download_path = self.music_path / f'{title}_{artist}.%(ext)s'
                try:
                    with yt_dlp.YoutubeDL(self._create_yt_dlp_options(title, artist, album, key, str(download_path), False, True)) as ydl:
                        print(f'{self.download_songs.__name__} Downloading {title} {artist} ...')
                        ydl.download(url)
                        print(f'{self.download_songs.__name__} Successfully downloaded {title} {artist}')
                except Exception as e:
                    failed_downloads[key] = song
                    print(f'Error downloading {title} {artist} due to {e}')

            if failed_downloads:
                with Path('./Data/Failed.json').open('w') as fp:
                    json.dump(failed_downloads, fp, indent=4)
                print(f'{self.download_songs.__name__} Failed downloading all songs. {len(failed_downloads)} songs failed to download.')
        except Exception as e:
            print(f'{self.download_songs.__name__} failed due to exception: {e}')

    async def download_from_yt_playlist(self, playlist_id):
        try:
            playlist_url = self.helpers.get_yt_playlist_url(playlist_id)
            print(f'{self.download_from_yt_playlist.__name__} starting download from playlist {playlist_url}')
            self.music_path.mkdir(parents=True, exist_ok=True)
            with yt_dlp.YoutubeDL(self._create_yt_dlp_options(path=str(self.music_path), set_thumbnail=True, playlist_id=playlist_id)) as ydl:
                ydl.download([playlist_url])

            print(f'{self.download_from_yt_playlist.__name__} success')
        except Exception as e:
            print(f'{self.download_from_yt_playlist.__name__} failed: {e}')

    def _find_matching_yt_link(self, search_results, song_duration, song_title):
        for search_result in search_results['videos']:
            yt_song_title = search_result['title']
            is_song_in_correct_locale = self.helpers.song_is_correct_locale(song_title, yt_song_title)
            if is_song_in_correct_locale and self.helpers.is_song_duration_within_threshold(song_duration, self.small_threshold, search_result['duration']):
                return self.helpers.get_complete_yt_url(search_result)
        
        return None
    
    def _get_current_downloaded_songs(self):
        currently_downloaded_songs = {}
        try:
            if not self.music_path.exists():
                return currently_downloaded_songs

            files = [f for f in listdir(self.music_path) if isfile(join(self.music_path, f))]

            if files:
                for song_file in files:
                    if song_file.endswith(".mp3"):
                        audio = MP3(str(self.music_path / song_file))

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

                        currently_downloaded_songs[info['description']] = info['title']

            return currently_downloaded_songs
        except:
            print(f'{self._get_current_downloaded_songs.__name__} Could not access downloaded files')

    def _create_yt_dlp_options(self, title='', artist='', album='', key='', path='', playlist_id='', set_thumbnail=False, manually_set_metadata=False):
        archive_path = self.archive_folder_path / ('archive.txt' if playlist_id == '' else f'{playlist_id}.txt')
        archive_path.parent.mkdir(parents=True, exist_ok=True)

        outtmpl_path = Path(path) if path else self.music_path

        options = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s_%(album)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'verbose': False,
            'ignoreerrors': 'only_download',
            'skip_unavailable_fragments': True,
            'download_archive': str(archive_path),
            'outtmpl': str(outtmpl_path / '%(title)s_%(album)s.%(ext)s'),
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

        if manually_set_metadata:
            options['postprocessor_args'] = {
                    'FFmpegMetadata': [
                        '-metadata', f'title={title}',
                        '-metadata', f'artist={artist}',
                        '-metadata', f'album={album}',
                        '-metadata', f'description={key}',
                    ]
                }
        else:
            options['postprocessors'].extend([
                {
                    'key': 'FFmpegMetadata',
                    'add_metadata': True
                }
            ])

        if set_thumbnail:
            post_processor_arg = {
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

            if 'postprocessor_args' in options:
                options['postprocessor_args'].update(post_processor_arg)
            else:
                options['postprocessor_args'] = post_processor_arg
            
        return options
