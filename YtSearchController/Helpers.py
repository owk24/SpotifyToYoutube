import json
import re
import sys

sys.path.append("./")
from youtube_search import YoutubeSearch

import Constants.LocaleNames as LocaleNames
from Constants.LocaleEnum import LocaleEnum
from Constants.Regexes import LocaleSongTitleRegex

class Helpers:
    def SongIsCorrectLocale(self, fileSongName, ytSongName):
        fileSongLocale = self.GetSongLocaleFromSong(fileSongName)
        ytSongLocale = self.GetSongLocaleFromSong(ytSongName)

        return fileSongLocale == ytSongLocale

    def GetSongLocaleFromSong(self, ytSongName):
        ytMatch = re.search(LocaleSongTitleRegex, ytSongName, re.IGNORECASE)
        songLocale = LocaleEnum.KOREAN.name
        if ytMatch:
            languageCode = ytMatch.group(1)
            if languageCode == LocaleNames.EnglishFull or languageCode == LocaleNames.EnglishPart:
                songLocale = LocaleEnum.ENGLISH.name
            elif languageCode == LocaleNames.JapaneseFull or languageCode == LocaleNames.JapanesePart:
                songLocale = LocaleEnum.JAPANESE.name
        
        return songLocale

    def GetYtSearchResults(self, searchRequest, maxResults):
        searchResultOfficialJsonString = YoutubeSearch(searchRequest, max_results=maxResults).to_json()
        searchResultJsons = json.loads(searchResultOfficialJsonString)
        return searchResultJsons

    def IsSongDurationWithinThreshold(self, songDuration, threshold, ytDuration):
        return songDuration - threshold <= self.GetDecimalDurationFormat(ytDuration) and self.GetDecimalDurationFormat(ytDuration) <= songDuration + threshold

    def GetDecimalDurationFormat(self, duration):
        times = duration.split(':')
        minute = int(times[0])
        seconds = int(times[1])

        return float(minute + seconds/60)
    
    def GetCompleteYtUrl(self, searchResultToUse):
        urlSuffix = searchResultToUse["url_suffix"]
        completeUrl = "https://www.youtube.com" + urlSuffix

        return completeUrl
    
    def GetYtPlaylistUrl(self, playlistId):
        return f"https://www.youtube.com/playlist?list={playlistId}"
