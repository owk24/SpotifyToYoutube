from get_cover_art import CoverFinder

class CoverArtController:
    def __init__(self):
        self.options = {
            'cleanup': True
        }

    # from apple music api, heavily rate limited
    def get_album_art(self, folder_path):
        finder = CoverFinder(self.options)
        finder.scan_folder(folder_path)
