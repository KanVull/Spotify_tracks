class Track:
    def __init__(self, name, artist, time, downloaded, playlists):
        self.name = name
        self.artist = artist
        self.time = time
        self.downloaded = downloaded
        self.playlists = playlists

    def to_mp3_name(self):
        return f'{self.artist} - {self.name}.mp3'    


