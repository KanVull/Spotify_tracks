from PyQt5 import QtCore
from PyQt5 import Qt
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel, QCheckBox

import os
import sys
import pyperclip
import webbrowser
import configparser
from work_xml import SpotifyListener

class TrackWidget(QWidget):
    def __init__(self, track, parent=None):
        QWidget.__init__(self, parent=parent)

        self.track = track
        prepairedName = self.track.name.lower().replace('&', '%26')
        prepairedArtist = self.track.artist.lower().replace('&', '%26')
        self.links = {
            'KissVK': f"https://kissvk.com/?search={prepairedArtist.replace(' ', '%20')}%20-%20{prepairedName.replace(' ', '%20')}",
            'YouTube': f"https://www.youtube.com/results?search_query={prepairedArtist.replace(' ', '+')}+-+{prepairedName.replace(' ', '+')}",
        }

        self.setupUI()

    def setupUI(self):
        self.setMinimumSize(Qt.QSize(0,70))
        self.setMaximumSize(Qt.QSize(16777215, 70))

        self.widgetlayout = QHBoxLayout(self)

        self.layoutnames = QVBoxLayout()
        self.layoutnames.setSpacing(0)
        self.layoutnames.setObjectName('layoutnames')

        self.labelname = QLabel(self)
        self.labelname.setScaledContents(True)
        self.labelname.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.labelname.setWordWrap(True)
        self.labelname.setMargin(0)
        self.labelname.setIndent(-1)
        self.labelname.setText(self.track.name)
        self.labelname.setObjectName('labelname')

        self.labelartist = QLabel(self)
        self.labelartist.setText(self.track.artist)
        self.labelartist.setObjectName('labelartist')

        self.labelplaylists = QLabel(self)
        self.labelplaylists.setText(', '.join(self.track.playlists))
        self.labelplaylists.setObjectName('labelplaylists')

        self.layoutnames.addWidget(self.labelname)
        self.layoutnames.addWidget(self.labelartist)
        self.layoutnames.addWidget(self.labelplaylists)
        self.layoutnames.setContentsMargins(0,0,0,0)
        

        self.layoutButtonsInfo = QVBoxLayout()
        self.layoutButtonsInfo.setObjectName('layoutbuttonsinfo')

        self.labeltime = QLabel(self)
        self.labeltime.setText(self.track.time)
        self.labeltime.setObjectName('labeltime')

        self.checkout = QCheckBox(self)
        self.checkout.setObjectName("checkbox")
        self.checkout.setToolTip('downloaded')
        if self.track.downloaded:
            self.checkout.setChecked(True)   
        self.checkout.stateChanged.connect(self.changeCheckStatus)   

        self.labelinfo = QLabel(self)
        self.labelinfo.setText(f'Добавлен: {self.track.date}')
        self.labelinfo.setObjectName('labelinfo')

        self.layoutButtonsInfo.addWidget(self.labeltime)
        self.layoutButtonsInfo.addWidget(self.checkout)
        self.layoutButtonsInfo.addWidget(self.labelinfo)
        self.layoutButtonsInfo.setContentsMargins(0,0,0,0)


        self.widgetlayout.addLayout(self.layoutnames)
        self.widgetlayout.addLayout(self.layoutButtonsInfo)
        self.widgetlayout.setStretch(0, 50)
        self.widgetlayout.setContentsMargins(6,3,6,3)
        
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setObjectName("trackwidget")
        self.setToolTip(f'{self.track.get_name()}\n(double click to copy to clipboard)')
        self.installEventFilter(self)

        self.setAcceptDrops(True)

        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        for key in self.links.keys():
            action = QtWidgets.QAction(self)
            action.setText(key)
            action.triggered.connect(self.download)
            self.addAction(action)
    

    def download(self):
        sender = self.sender()
        webbrowser.open(self.links[sender.text()])

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super(TrackWidget, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        super(TrackWidget, self).dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                self.changeFileProperties(url.path())
            event.acceptProposedAction()
        else:
            super(TrackWidget,self).dropEvent(event)

    def changeFileProperties(self, path):
        if path[-3:] != 'mp3':
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Warning)
            msgBox.setText("Its not a mp3 file")
            msgBox.setWindowTitle("Error")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msgBox.exec()
        else:
            new_path = path[1:path.rfind('/') + 1] + self.track.to_mp3_name()
            os.rename(path[1:], new_path)
            self.checkout.setChecked(True)

    def eventFilter(self, obj, event):
        if obj == self and event.type() == QtCore.QEvent.MouseButtonDblClick:
            self.onClicked()     
        return super(TrackWidget, self).eventFilter(obj, event)

    def onClicked(self):
        pyperclip.copy(self.track.get_name())
        
    def changeCheckStatus(self, state):
        if state == QtCore.Qt.Checked:
            main = self.parent()
            self.track.downloaded = True
            while type(main) != Main:
                main = main.parent()
            if main.filterDownloaded.checkState() == QtCore.Qt.Checked:
                self.hide()
        else:
            self.track.downloaded = False
        scroll = self.parent()
        while type(scroll) != scrollAreaTracks:
            scroll = scroll.parent()
        scroll.spl.changeStatus(self.track.track_id, True if state == 2 else False)          

class scrollAreaTracks(QScrollArea):
    def __init__(self, spl, parent=None):
        QScrollArea.__init__(self, parent=parent)
        self.spl = spl
        self.setupUI()

    def setupUI(self):
        self.setObjectName("scrollarea")
        self.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContentsLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.scrollAreaWidgetContentsLayout.setContentsMargins(0,0,0,0)
        self.scrollAreaWidgetContentsLayout.setSpacing(0)
        for track in self.spl.list_of_tracks:
            self.scrollAreaWidgetContentsLayout.addWidget(TrackWidget(track))
        self.setWidget(self.scrollAreaWidgetContents)


class Ui_Form(object):
    def setupUi(self, MainWindow):
        MainWindow.setWindowTitle("Your Spoty")
        MainWindow.setObjectName("form")
        MainWindow.resize(800, 800)
        MainWindow.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName('centralwidget')
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setContentsMargins(0,0,0,0)
        self.centralWidgetLayout = QVBoxLayout(self.centralWidget)
        self.centralWidgetLayout.setContentsMargins(0,0,0,0)

        self.config = configparser.ConfigParser()
        if os.path.exists('config.ini'):
            self.config.read("config.ini")
        else:
            self.createConfig()

        if self.config['KEYS']['client_id'] == '' or self.config['KEYS']['client_secret'] == '':
            self.setupSpotifyError()
        else:
            self.setupList()

        MainWindow.setCentralWidget(self.centralWidget)
        MainWindow.setContentsMargins(0,0,0,0)

    def changeCheckStatus(self, state):
        for widget in self.scrollArea.widget().children():
            if type(widget) != TrackWidget:
                continue
            if state == QtCore.Qt.Checked:
                if widget.track.downloaded == True:
                    widget.hide()
            else:
                widget.show()

    def createConfig(self):
        self.config['KEYS'] = {
            'client_id': '',
            'client_secret': '',
            'redirect_uri': 'https://mysite.com'
        } 
        self.config['PATHS'] = {
            'path_of_downloads': ''
        }
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    def createEmptyXml(self):
        with open('allTracks.xml', 'w') as xmlfile:
            xmlfile.write("<?xml version='1.0' encoding='utf-8'?><tracks count='0'></tracks>")

    def setupList(self):
        spl = SpotifyListener(self.config['KEYS']['client_id'], self.config['KEYS']['client_secret'], self.config['KEYS']['redirect_uri'])
        if not os.path.exists('allTracks.xml'):
            self.createEmptyXml()
        spl.setXMLFile('allTracks.xml')
        spl.Load_list()    
        self.scrollArea = scrollAreaTracks(spl, self.centralWidget)  

        self.filtersLayout = QHBoxLayout()
        self.filtersLayout.setContentsMargins(10,0,0,8)
        self.filterDownloaded = QCheckBox(self.centralWidget) 
        self.filterDownloaded.setText('Only not downloaded')
        self.filterDownloaded.setToolTip('Show only not downloaded') 
        self.filterDownloaded.stateChanged.connect(self.changeCheckStatus) 
        self.filtersLayout.addWidget(self.filterDownloaded)

        self.verticalLayout.addWidget(self.scrollArea)
        self.verticalLayout.addLayout(self.filtersLayout)
        self.verticalLayout.setContentsMargins(0,0,0,0)
        self.centralWidgetLayout.addLayout(self.verticalLayout)
        self.centralWidgetLayout.setContentsMargins(0,0,0,0)

    def setupSpotifyError(self):
        self.errorWindow = QWidget(self.centralWidget)
        self.errorWindowLayout = QVBoxLayout()
        label = QLabel(self.centralWidget)
        label.text = 'You need to config with app by addition your spotify client app data into config.ini file'
        # label.setAlignment()

        self.verticalLayout.addWidget(self.errorWindow)
        self.verticalLayout.setContentsMargins(0,0,0,0)
        self.centralWidgetLayout.addLayout(self.verticalLayout)
        self.centralWidgetLayout.setContentsMargins(0,0,0,0)


class Main(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent) 
        self.setupUi(self)        

if __name__ == '__main__':
    styleWidget = '''
            #scrollarea, #trackwidget, #listwidget {
                background-color: #ffffff;
                border-width: 0;
                padding: 0;
                margin: 0;
            }
            #trackwidget:hover {
                background-color: #efefef;
            }
            #labelname, #labeltime {
                font-weight: bold;
                font-size: 15px;
            }
            #labelartist {
                font-weight: 700;
                font-size: 12px;
            }
            #labelplaylists, #labelinfo {
                font-weight: 100;
                font-size: 10px;
            }
            #labeltime, #labelinfo {
                text-align: right;
            }
        '''
    app = Qt.QApplication(sys.argv)
    app.setStyleSheet(styleWidget)
    ex  = Main()
    ex.show()
    sys.exit(app.exec_()) 


