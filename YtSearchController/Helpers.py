import json
import re
import sys

sys.path.append("./")
from youtube_search import YoutubeSearch

import Constants.LocaleNames as LocaleNames
from Constants.LocaleEnum import LocaleEnum
from Constants.Regexes import LOCALE_SONG_TITLE_REGEX

class Helpers:
    def song_is_correct_locale(self, file_song_name, yt_song_name):
        file_song_locale = self.get_song_locale_from_song(file_song_name)
        yt_song_locale = self.get_song_locale_from_song(yt_song_name)

        return file_song_locale == yt_song_locale

    def get_song_locale_from_song(self, yt_song_name):
        yt_match = re.search(LOCALE_SONG_TITLE_REGEX, yt_song_name, re.IGNORECASE)
        song_locale = LocaleEnum.KOREAN.name
        if yt_match:
            language_code = yt_match.group(1)
            if language_code == LocaleNames.ENGLISH_FULL or language_code == LocaleNames.ENGLISH_PART:
                song_locale = LocaleEnum.ENGLISH.name
            elif language_code == LocaleNames.JAPANESE_FULL or language_code == LocaleNames.JAPANESE_PART:
                song_locale = LocaleEnum.JAPANESE.name
        
        return song_locale

    def get_yt_search_results(self, search_request, max_results):
        search_result_official_json_string = YoutubeSearch(search_request, max_results=max_results).to_json()
        search_result_jsons = json.loads(search_result_official_json_string)
        return search_result_jsons

    def is_song_duration_within_threshold(self, song_duration, threshold, yt_duration):
        return song_duration - threshold <= self.get_decimal_duration_format(yt_duration) and self.get_decimal_duration_format(yt_duration) <= song_duration + threshold

    def get_decimal_duration_format(self, duration):
        times = duration.split(':')
        minute = int(times[0])
        seconds = int(times[1])

        return float(minute + seconds/60)
    
    def get_complete_yt_url(self, search_result_to_use):
        url_suffix = search_result_to_use["url_suffix"]
        complete_url = "https://www.youtube.com" + url_suffix

        return complete_url
    
    def get_yt_playlist_url(self, playlist_id):
        return f"https://www.youtube.com/playlist?list={playlist_id}"
