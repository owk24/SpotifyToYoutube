import asyncio

from SpotifyApiController.SpotifyApiController import SpotifyApiController
from YtSearchController.YouTubeApiController import YouTubeApiController
from YtMusicApiController.YtMusicController import YtMusicController

async def main():
    # spotify_api_controller = SpotifyApiController()
    # spotify_api_controller.get_song_data_from_user_liked_list()

    youtube_api_controller = YouTubeApiController()
    # await youtube_api_controller.get_youtube_links_from_songs()

asyncio.run(main())