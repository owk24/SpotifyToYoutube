import asyncio

from SpotifyApiController.SpotifyApiController import SpotifyApiController
from YtSearchController.YouTubeApiController import YouTubeApiController
from YtMusicApiController.YtMusicController import YtMusicController

async def main():
    # spotifyApiController = SpotifyApiController()
    # spotifyApiController.GetSongDataFromUserLikedList()

    youtubeApiController = YouTubeApiController()
    # await youtubeApiController.GetYoutubeLinksForSongs()

asyncio.run(main())