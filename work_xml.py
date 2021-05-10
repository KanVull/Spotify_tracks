import datetime
import configparser
import xml.etree.ElementTree as ET
from track import Track
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifyListener():
    def __init__(self, client_id, client_secret, redirect_uri):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope="user-library-read"))
        if self.sp:
            pass
        self.playlists = self.Load_playlists()

    def setXMLFile(self, path):
        self.path = path
        self.tree = ET.parse(path)
        self.root = self.tree.getroot()

    def Load_playlists(self):
        results = self.sp.current_user_playlists(limit=100, offset=0)
        playlists = results['items']
        dict_playlists = {playlist['name']: [] for playlist in playlists}
        for playlist in playlists:
            for i in range(0, 10000, 100):
                tracks = sp.playlist_tracks(playlist['id'], limit=100, offset=i)
                if not tracks['items']:
                    break
                dict_playlists[playlist['name']] += [track['track']['id'] for track in tracks['items']]
        return dict_playlists

    def Load_list(self):
        list_of_tracks = []
        for i in range(0,100000,50):
            results = self.sp.current_user_saved_tracks(limit=50, offset=i)
            if not results['items']:
                break
            
            for idx, item in enumerate(results['items']):
                track = item['track']
                track_in_xml = self.root.findall(f'./track[@id="{track["id"]}"]')
                current_playlists = self.getPlaylistsOfTrack(track['id'])
                if track_in_xml:
                    _id = track_in_xml[0].attrib['id']
                    _name = track_in_xml[0].find('name').text
                    _artict = track_in_xml[0].find('artist').text
                    _time = track_in_xml[0].find('time').text
                    _downloaded = track_in_xml[0].attrib['downloaded']
                    _playlists = track_in_xml[0].find('playlists').findall('playlist')
                    _playlists = [pl.text for pl in _playlists]
                    differense = [x for x in _playlists + current_playlists if x not in _playlists or x not in current_playlists]
                    if len(differense):
                        parent = track_in_xml[0].find('playlists')
                        for element in parent.findall('playlist'):
                            parent.remove(element)
                        for playlist in playlists:
                            _new_playlist = ET.SubElement(parent, 'playlist')
                            _new_playlist.text = playlist
                        parent.set('count', str(len(playlists)))
                    _playlists = current_playlists                
                    _date = track_in_xml[0].attrib['when']
                    list_of_tracks.append(Track(_id, _name, _artict, _time, _downloaded, _playlists, _date))
                    continue
                
                trackET = ET.SubElement(self.root, 'track')
                trackETName = ET.SubElement(trackET, 'name')
                trackETArtist = ET.SubElement(trackET, 'artist')
                trackETTime = ET.SubElement(trackET, 'time')
                trackETPlaylists = ET.SubElement(trackET, 'playlists')
                trackETPlaylists.set('count', str(len(playlists)))
                for playlist in current_playlists:
                    p = ET.SubElement(trackETPlaylists, 'playlist')
                    p.text = playlist
                trackET.set('id', track['id'])    
                trackET.set('downloaded', 'False')
                trackET.set('when', datetime.datetime.now().strftime("%d %B %Y"))
                trackETName.text = track['name']
                trackETArtist.text = track['artists'][0]['name']
                millis = int(track['duration_ms'])
                seconds = (millis / 1000) % 60
                seconds = int(seconds)
                minutes = (millis / (1000 * 60)) % 60
                minutes = int(minutes)
                trackETTime.text = '%02d:%02d' % (minutes, seconds)
                list_of_tracks.append(Track(track['id'], track['name'], track['artists'][0]['name'], '%02d:%02d' % (minutes, seconds), False, playlists, datetime.datetime.now().strftime("%d %B %Y")))

        self.root.set('count', str(len(list_of_tracks)))
        self.indent(root)
        self.tree.write('allTracks.xml', encoding='utf-8', xml_declaration=True)

        return list_of_tracks

    def indent(self, elem, level=0):
        i = "\n" + level * "    "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "    "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def getPlaylistsOfTrack(self, track_id):
        names = list()
        for name, tracks_list in self.playlists.items():
            if track_id in tracks_list:
                names.append(name)
                continue
        return names    

    def changeStatus(self, track_id, status):
        track_in_xml = self.froot.findall(f'./track[@id="{track_id}"]')
        track_in_xml[0].set('downloaded', str(status))
        self.tree.write(self.path, encoding='utf-8', xml_declaration=True)