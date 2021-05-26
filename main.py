from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow, 
    QDialog, 
    QDialogButtonBox,
    QMessageBox,
    QVBoxLayout, 
    QHBoxLayout,
    QFormLayout, 
    QWidget,
    QPushButton,
    QAction, 
    QScrollArea, 
    QLabel, 
    QCheckBox,
    QLineEdit,
)
import os
import sys
import pyperclip
import webbrowser
import configparser
from work_xml import SpotifyListener

if not os.path.exists('C:/ProgramData/Your Spoti'):
    os.mkdir('C:/ProgramData/Your Spoti')
CONFIG_PATH = 'C:/ProgramData/Your Spoti/config.ini'
ALLTRACKS_PATH = 'C:/ProgramData/Your Spoti/allTracks.xml'
CACHE_PATH = 'C:/ProgramData/Your Spoti/.cache'

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
        self.setMinimumSize(QtCore.QSize(0,70))
        self.setMaximumSize(QtCore.QSize(16777215, 70))

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
            action = QAction(self)
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
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText("Its not a mp3 file")
            msgBox.setWindowTitle("Error")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec()
        else:
            config = configparser.ConfigParser()
            config.read(CONFIG_PATH)
            if config['FILTERS']['rename_always'] == '1':
                rename(path, self.track)
                self.checkout.setChecked(True)
            elif config['FILTERS']['replace_always'] == '1':
                replace(path, self.track)
                self.checkout.setChecked(True)
            else:        
                rename_replace_window = ReplacingWindow(self.track, path)
                if rename_replace_window.exec_():
                    self.checkout.setChecked(True)
            mainwindow = self.parent()
            while type(mainwindow) != Main:
                mainwindow = mainwindow.parent()
            mainwindow.config.read(CONFIG_PATH)
            mainwindow.setNameOfRenameReplace_button()           

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


class LoadSpotifyTracks_QObject(QtCore.QObject):
    loaded_list = QtCore.pyqtSignal(SpotifyListener)
    
    def __init__(self, config):
        QtCore.QObject.__init__(self)
        self.config = config

    def createEmptyXml(self):
        with open(ALLTRACKS_PATH, 'w') as xmlfile:
            xmlfile.write("<?xml version='1.0' encoding='utf-8'?><tracks count='0'></tracks>")

    def run(self):
        spl = SpotifyListener(self.config['KEYS']['client_id'], self.config['KEYS']['client_secret'], self.config['KEYS']['redirect_uri'], CACHE_PATH)
        if not os.path.exists(ALLTRACKS_PATH):
            self.createEmptyXml()
        spl.Load_playlists()
        spl.setXMLFile(ALLTRACKS_PATH)
        spl.Load_list()
        self.loaded_list.emit(spl)    


def rename(filename, track):
    new_path = filename[1:filename.rfind('/') + 1] + track.to_mp3_name()
    os.rename(filename[1:], new_path)

def replace(filename, track):
    folder = str(QFileDialog.getExistingDirectory(None, "Select Directory"))
    os.replace(filename[1:], folder + '/' + track.to_mp3_name())


class UI_ReplacingWindow(object):
    def setupUI(self, Window, track_data, file_data):
        self.track = track_data
        self.file = file_data

        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_PATH)

        self.windowlauoyt = QVBoxLayout(Window)
        Window.setWindowTitle("Rename and Replace")
        Window.setFixedSize(QtCore.QSize(300, 200))
        self.create_layout()   

    def create_layout(self):
        labelBefore = QLabel()
        labelBefore.setText(self.file.split('/')[-1])
        labelTO = QLabel()
        labelTO.setText('TO')
        labelAfter = QLabel()
        labelAfter.setText(self.track.to_mp3_name())
        labelBefore.setFont(QtGui.QFont('Arial', 12))
        labelBefore.setAlignment(QtCore.Qt.AlignCenter)
        labelBefore.setWordWrap(True)
        labelTO.setFont(QtGui.QFont('Arial', 8))
        labelTO.setAlignment(QtCore.Qt.AlignCenter)
        labelAfter.setFont(QtGui.QFont('Arial', 12))
        labelAfter.setAlignment(QtCore.Qt.AlignCenter)
        labelAfter.setWordWrap(True)

        btnRename = QPushButton()
        btnRename.setText('Rename')
        btnRename.clicked.connect(lambda: self.rename_replace(True))
        btnReplace = QPushButton()
        btnReplace.setText('Rename and Replace')
        btnReplace.clicked.connect(lambda: self.rename_replace(False))

        self.checkout = QCheckBox()
        self.checkout.setText('Don\'t ask again')

        btnBox = QDialogButtonBox()
        btnBox.setStandardButtons(
            QDialogButtonBox.Cancel
        )
        btnBox.rejected.connect(self.reject)

        self.windowlauoyt.addWidget(labelBefore)
        self.windowlauoyt.addWidget(labelTO)
        self.windowlauoyt.addWidget(labelAfter)
        self.windowlauoyt.addWidget(btnRename)
        self.windowlauoyt.addWidget(btnReplace)
        self.windowlauoyt.addWidget(self.checkout)
        self.windowlauoyt.addWidget(btnBox)

    def rename_replace(self, only_rename=True):
        if only_rename:
            rename(self.file, self.track)
        else:
            replace(self.file, self.track)
        if self.checkout.checkState() == QtCore.Qt.Checked:
            self.config['FILTERS']['rename_always'] = '1' if only_rename else '0'
            self.config['FILTERS']['replace_always'] = '0' if only_rename else '1'
            with open(CONFIG_PATH, 'w') as configfile:
                self.config.write(configfile)
        self.accept()              

    def reject(self):
        self.reject()


class ReplacingWindow(QDialog, UI_ReplacingWindow):
    def __init__(self, track_data, file_data, parent=None):
        super(ReplacingWindow, self).__init__(parent, QtCore.Qt.WindowStaysOnTopHint)
        self.setupUI(self, track_data, file_data)


class UI_ReplacingConfig(object):
    def setupUI(self, Window):
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_PATH)

        self.windowlauoyt = QVBoxLayout(Window)
        Window.setWindowTitle("Rename and Replace")
        Window.resize(QtCore.QSize(300, 200))
        hint = QLabel()
        hint.setText('What to do when dragging and dropping a file into the program')
        hint.setAlignment(QtCore.Qt.AlignCenter)
        hint.setWordWrap(True)
        ask_btn = QPushButton()
        ask_btn.setText('Ask')
        ask_btn.clicked.connect(lambda: self.change(0))
        rename_btn = QPushButton()
        rename_btn.setText('Rename')
        rename_btn.clicked.connect(lambda: self.change(1))
        replace_btn = QPushButton()
        replace_btn.setText('Replace')
        replace_btn.clicked.connect(lambda: self.change(2))
        self.windowlauoyt.addWidget(hint)
        self.windowlauoyt.addWidget(ask_btn)
        self.windowlauoyt.addWidget(rename_btn)
        self.windowlauoyt.addWidget(replace_btn)

    def change(self, state):
        if state == 0:
            self.config['FILTERS']['rename_always'] = self.config['FILTERS']['replace_always'] = '0'
        elif state == 1:
            self.config['FILTERS']['rename_always'] = '1'
            self.config['FILTERS']['replace_always'] = '0'
        elif state == 2:
            self.config['FILTERS']['rename_always'] = '0'
            self.config['FILTERS']['replace_always'] = '1'
        with open(CONFIG_PATH, 'w') as configfile:
            self.config.write(configfile)    
        self.accept()                


class ReplacingConfig(QDialog, UI_ReplacingConfig):
    def __init__(self, parent=None):
        super(ReplacingConfig, self).__init__(parent)
        self.setupUI(self)


class UI_EnterSpotifyDataQDialog(object):
    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()      
    
    def loadKeysLayout(self):
        formwidget = QWidget()
        formLayout = QFormLayout(formwidget)
        formLayout.setContentsMargins(0,0,0,0)
        self.client_id_LineEdit = QLineEdit()
        self.client_secret_LineEdit = QLineEdit()
        self.redirect_uri_LineEdit = QLineEdit()
        self.redirect_uri_LineEdit.setText('http://localhost:8080')
        hint = QLabel()
        hint.setText('Add http://localhost:8080 in your spotify app in Redirect URL or change for your custom')
        hint.setWordWrap(True)
        formLayout.addRow('Client ID', self.client_id_LineEdit)
        formLayout.addRow('Client Secret', self.client_secret_LineEdit)
        formLayout.addRow('Redirect URI', self.redirect_uri_LineEdit)
        formLayout.addRow('', hint)

        btnBox = QDialogButtonBox()
        btnBox.setStandardButtons(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        btnBox.accepted.connect(self.set_keys)
        btnBox.rejected.connect(self.reject)
        self.windowlauoyt.addWidget(formwidget)
        self.windowlauoyt.addWidget(btnBox)

    def setupUI(self, Window):
        webbrowser.open('https://developer.spotify.com/dashboard/applications')
        self.windowlauoyt = QVBoxLayout(Window)
        Window.setWindowTitle('Enter your spotify data')
        Window.setFixedSize(QtCore.QSize(400, 160))
        self.loadKeysLayout()
        
    def set_keys(self):
        client_id = self.client_id_LineEdit.text()
        client_secret = self.client_secret_LineEdit.text()
        redirect_uri = self.redirect_uri_LineEdit.text()

        if client_id == '' or client_secret == '' or redirect_uri == '':
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText('Data Incorrect')
            msgBox.setWindowTitle('Error')
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec()
        else:
            self.client_id = client_id
            self.client_secret = client_secret
            self.redirect_uri = redirect_uri
            self.set_token()

    def set_token(self):
        self.accept()

    def reject(self):
        self.reject()

    def getValues(self):
        return {
            'client_id': self.client_id, 
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
        }


class EnterSpotifyDataQDialog(QDialog, UI_EnterSpotifyDataQDialog):
    def __init__(self, parent=None):
        super(EnterSpotifyDataQDialog, self).__init__(parent)
        self.setupUI(self)


class Ui_Form(object):
    def setupUI(self, MainWindow):

        self.config = configparser.ConfigParser()
        if os.path.exists(CONFIG_PATH):
            self.config.read(CONFIG_PATH)
        else:
            self.createConfig()

        self.MainWindow = MainWindow
        self.setNameOfWindow()
        self.MainWindow.setObjectName('form')
        self.MainWindow.resize(800, 800)
        self.MainWindow.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.centralWidget = QWidget(self.MainWindow)
        self.centralWidget.setObjectName('centralwidget')
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setContentsMargins(0,0,0,0)
        self.centralWidgetLayout = QVBoxLayout(self.centralWidget)
        self.centralWidgetLayout.setContentsMargins(0,0,0,0)

        if not os.path.exists(CACHE_PATH):
            self.setupSpotifyError()
        else:
            self.setupList()

    def setNameOfWindow(self):
        if self.config['USER']['user_name'] == '':
            self.MainWindow.setWindowTitle('Your Spoti')
        else:
            self.MainWindow.setWindowTitle('Your Spoti | ' + self.config['USER']['user_name'])    

    def changeCheckStatus(self, state):
        self.config['FILTERS']['only_downloaded'] = '1' if state == QtCore.Qt.Checked else '0'
        with open(CONFIG_PATH, 'w') as configfile:
            self.config.write(configfile)
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
            'redirect_uri': 'http://localhost:8080',
        }
        self.config['USER'] = {
            'user_name': '',
        } 
        self.config['FILTERS'] = {
            'only_downloaded': '0',
            'rename_always': '0',
            'replace_always': '0',
        }
        with open(CONFIG_PATH, 'w') as configfile:
            self.config.write(configfile)

    def setupList(self):
        self.setNameOfWindow()
        self.thread = QtCore.QThread()
        self.loadSpotifyTracks_QObject = LoadSpotifyTracks_QObject(self.config)
        self.loadSpotifyTracks_QObject.moveToThread(self.thread)
        self.loadSpotifyTracks_QObject.loaded_list.connect(self.setScrollArea)
        self.thread.started.connect(self.setLoadingScreen)
        self.thread.started.connect(self.loadSpotifyTracks_QObject.run)
        self.thread.start()
        
    def setLoadingScreen(self):
        self.clearLayout(self.verticalLayout)
        loadingLabel = QLabel(self.centralWidget)
        loadingLabel.setText('Loading Your Playlist')
        loadingLabel.setFont(QtGui.QFont('Arial', 25))
        loadingLabel.setAlignment(QtCore.Qt.AlignCenter)

        horizontalLabel = QHBoxLayout()
        gifLabel = QLabel(self.centralWidget)
        gifLabel.setMinimumSize(QtCore.QSize(180, 85))
        gifLabel.setMaximumSize(QtCore.QSize(180, 85))
        gifLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.movie = QtGui.QMovie('loading.gif')
        gifLabel.setMovie(self.movie)
        horizontalLabel.addStretch(0)
        horizontalLabel.addWidget(gifLabel)
        horizontalLabel.addStretch(0)
        self.movie.start()

        self.verticalLayout.addStretch(0)
        self.verticalLayout.addWidget(loadingLabel)
        self.verticalLayout.addLayout(horizontalLabel)
        self.verticalLayout.addStretch(0)
        self.setMyCentralWidget()

    def setScrollArea(self, spl):
        self.config['USER']['user_name'] = spl.user_name
        with open(CONFIG_PATH, 'w') as configfile:
            self.config.write(configfile)
        self.setNameOfWindow()    
        self.clearLayout(self.verticalLayout)
        self.scrollArea = scrollAreaTracks(spl, self.centralWidget) 
        self.filtersLayout = QHBoxLayout()
        self.filtersLayout.setContentsMargins(10, 0, 0, 8)
        self.filterDownloaded = QCheckBox(self.centralWidget) 
        self.filterDownloaded.setText('Only not downloaded')
        self.filterDownloaded.setToolTip('Show only not downloaded') 
        self.filterDownloaded.stateChanged.connect(self.changeCheckStatus)
        self.filterDownloaded.setChecked(True if self.config['FILTERS']['only_downloaded'] == '1' else False)
        self.buttonRenameReplace = QPushButton(self.centralWidget)
        self.buttonRenameReplace.setToolTip('Drag and Drop configuration') 
        self.setNameOfRenameReplace_button()
        self.buttonRenameReplace.clicked.connect(self.Rename_Replace_config)
        self.filtersLayout.addWidget(self.filterDownloaded)
        self.filtersLayout.addStretch(0)
        self.filtersLayout.addWidget(self.buttonRenameReplace)
        self.verticalLayout.addWidget(self.scrollArea)
        self.verticalLayout.addLayout(self.filtersLayout)
        self.movie.stop()
        self.setMyCentralWidget()

    def setNameOfRenameReplace_button(self):
        if self.config['FILTERS']['rename_always'] == '1':
            self.buttonRenameReplace.setText('Rename')
        elif self.config['FILTERS']['replace_always'] == '1':
            self.buttonRenameReplace.setText('Replace')
        else:        
            self.buttonRenameReplace.setText('Ask')

    def Rename_Replace_config(self):
        window = ReplacingConfig()
        if window.exec_():
            self.config.read(CONFIG_PATH)
            self.setNameOfRenameReplace_button()

    def setupSpotifyError(self):
        labelWarning = QLabel(self.centralWidget)
        labelWarning.setText('You need to connect with app by addition your spotify client app data')
        labelWarning.setAlignment(QtCore.Qt.AlignCenter)

        labelInfo = QLabel(self.centralWidget)
        labelInfo.setText('Create your app with random name and get "client id" and "client secret"')
        labelInfo.setAlignment(QtCore.Qt.AlignCenter)

        buttonLink = QPushButton(self.centralWidget)
        buttonLink.setText('Create App')
        buttonLink.clicked.connect(self.creationSpotifyApp_Click)

        self.verticalLayout.addStretch()
        self.verticalLayout.addWidget(labelWarning)
        self.verticalLayout.addWidget(labelInfo)
        self.verticalLayout.addWidget(buttonLink)
        self.verticalLayout.addStretch()
        self.setMyCentralWidget()

    def setMyCentralWidget(self):
        self.verticalLayout.setContentsMargins(0,0,0,0)
        self.centralWidgetLayout.addLayout(self.verticalLayout)
        self.centralWidgetLayout.setContentsMargins(0,0,0,0)
        self.MainWindow.setCentralWidget(self.centralWidget)
        self.MainWindow.setContentsMargins(0, 0, 0, 0)

    def creationSpotifyApp_Click(self):
        enterSpotifyDataQDialog = EnterSpotifyDataQDialog()
        if enterSpotifyDataQDialog.exec_():
            values = enterSpotifyDataQDialog.getValues()
            self.config['KEYS']['client_id'] = values['client_id']
            self.config['KEYS']['client_secret'] = values['client_secret']
            self.config['KEYS']['redirect_uri'] = values['redirect_uri']
            with open(CONFIG_PATH, 'w') as configfile:
                self.config.write(configfile)      
            self.clearLayout(self.verticalLayout)
            self.setupList()

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()        


class Main(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent) 
        self.setupUI(self)        


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
    app = QApplication(sys.argv)
    app.setStyleSheet(styleWidget)
    app.setWindowIcon(QtGui.QIcon('spotiApp.ico'))
    ex = Main()
    ex.show()
    sys.exit(app.exec_()) 


