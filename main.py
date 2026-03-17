import asyncio

from SpotifyApiController.SpotifyApiController import SpotifyApiController
from YtSearchController.YouTubeApiController import YouTubeApiController
from YtMusicApiController.YtMusicController import YtMusicController

async def main():
    # spotifyApiController = SpotifyApiController()
    # spotifyApiController.GetSongDataFromUserLikedList()

    youtubeApiController = YouTubeApiController()
    # await youtubeApiController.GetYoutubeLinksForSongs()

    await youtubeApiController.download_from_yt_playlist("PL5pxc3TW-DLJKUUucvQYjQCN3qKidh3rN")

asyncio.run(main())