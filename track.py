class Track:
    def __init__(self, track_id, name, artists, time, downloaded, playlists, date):
        self.track_id = track_id
        self.name = name
        self.artists = artists
        self.time = time
        self.downloaded = True if downloaded == 'True' else False
        self.playlists = playlists
        self.date = date

    def transliterate(self, name):
        slovar = {'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e',
            'ж':'zh','з':'z','и':'i','й':'i','к':'k','л':'l','м':'m','н':'n',
            'о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h',
            'ц':'c','ч':'cz','ш':'sh','щ':'scz','ъ':'','ы':'y','ь':'','э':'e',
            'ю':'u','я':'ja', 'А':'A','Б':'B','В':'V','Г':'G','Д':'D','Е':'E','Ё':'E',
            'Ж':'ZH','З':'Z','И':'I','Й':'I','К':'K','Л':'L','М':'M','Н':'N',
            'О':'O','П':'P','Р':'R','С':'S','Т':'T','У':'U','Ф':'F','Х':'H',
            'Ц':'C','Ч':'CZ','Ш':'SH','Щ':'SCH','Ъ':'','Ы':'y','Ь':'','Э':'E',
            'Ю':'U','Я':'YA','ґ':'','ї':'', 'є':'','Ґ':'g','Ї':'i',
            'Є':'e', '—':'', '?': '', '/': '-'}
        for key in slovar:
            name = name.replace(key, slovar[key])
        return name

    def to_mp3_name(self):
        artist = self.artists[0]
        if len(self.artists) > 1:
            artist += ' feat. ' + ', '.join(self.artists[1:])
        return self.transliterate(f'{artist} - {self.name}.mp3')

    def get_name(self):
        return f'{self.artists[0]} - {self.name}'    



