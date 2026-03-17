from get_cover_art import CoverFinder

class CoverArtController():
    options = {
        'cleanup': True
    }

    # from apple music api, heavily rate limited
    def get_album_art(self, folderPath):
        finder = CoverFinder(self.options)
        finder.scan_folder(folderPath)
