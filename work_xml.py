import datetime
import xml.etree.ElementTree as ET
from track import Track
import spotipy
from spotipy.oauth2 import SpotifyOAuth

tree = ET.parse('important_data.xml')
root = tree.getroot()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=root.find('client_id').text,
                                               client_secret=root.find('client_secret').text,
                                               redirect_uri=root.find('redirect_uri').text,
                                               scope="user-library-read"))

tree = ET.parse('allTracks.xml')
root = tree.getroot()

def Load_playlists():
    results = sp.current_user_playlists(limit=50, offset=0)
    playlists = results['items']
    dict_playlists = {playlist['name']: [] for playlist in playlists}
    for playlist in playlists:
        for i in range(0, 10000, 100):
            tracks = sp.playlist_tracks(playlist['id'], limit=100, offset=i)
            if not tracks['items']:
                break
            dict_playlists[playlist['name']] += [track['track']['id'] for track in tracks['items']]
    return dict_playlists

def Load_list():
    list_of_tracks = []
    for i in range(0,100000,50):
        results = sp.current_user_saved_tracks(limit=50, offset=i)
        if not results['items']:
            break
        
        for idx, item in enumerate(results['items']):
            track = item['track']
            track_in_xml = root.findall('./track/[name="{}"][artist="{}"]'.format(track["name"], track['artists'][0]['name']))
            if track_in_xml:
                _name = track_in_xml[0].find('name').text
                _artict = track_in_xml[0].find('artist').text
                _time = track_in_xml[0].find('time').text
                _downloaded = track_in_xml[0].attrib['downloaded']
                _playlists = track_in_xml[0].find('playlists').findall('playlist')
                _playlists = [pl.text for pl in _playlists]
                list_of_tracks.append(Track(_name, _artict, _time, _downloaded, _playlists))
                continue
            
            trackET = ET.SubElement(root, 'track')
            trackETName = ET.SubElement(trackET, 'name')
            trackETArtist = ET.SubElement(trackET, 'artist')
            trackETTime = ET.SubElement(trackET, 'time')
            trackETPlaylists = ET.SubElement(trackET, 'playlists')
            playlists = getPlaylistsOfTrack(track['id'])
            trackETPlaylists.set('count', str(len(playlists)))
            for playlist in playlists:
                p = ET.SubElement(trackETPlaylists, 'playlist')
                p.text = playlist
            trackET.set('downloaded', 'False')
            trackET.set('when', datetime.datetime.now().strftime("%d %B %Y %I:%M%p"))
            trackETName.text = track['name']
            trackETArtist.text = track['artists'][0]['name']
            millis = int(track['duration_ms'])
            seconds = (millis / 1000) % 60
            seconds = int(seconds)
            minutes = (millis / (1000 * 60)) % 60
            minutes = int(minutes)
            trackETTime.text = '%02d:%02d' % (minutes, seconds)
            list_of_tracks.append(Track(track['name'], track['artists'][0]['name'], '%02d:%02d' % (minutes, seconds), False, playlists))

    root.set('count', str(len(list_of_tracks)))
    indent(root)
    tree.write('allTracks.xml', encoding='utf-8', xml_declaration=True)

    return list_of_tracks
    # tree.write(tree, encoding='ascii', xml_declaration=True)

def indent(elem, level=0):
    i = "\n" + level*"    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def getPlaylistsOfTrack(track_id):
    names = []
    for name, tracks_list in playlists.items():
        if track_id in tracks_list:
            names.append(name)
            continue
    return names    
    
playlists = Load_playlists()