from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel, QCheckBox, QPushButton
from PyQt5.Qt import *
from tinytag import TinyTag

import os
import sys
import pyperclip
import webbrowser
import work_xml

class TrackWidget(QWidget):
    def __init__(self, Form, track):
        QWidget.__init__(self, parent=Form)

        self.track = track
        prepairedName = self.track.name.lower().replace('&', '%26')
        prepairedArtist = self.track.artist.lower().replace('&', '%26')
        self.links = {
            'KissVK': f"https://kissvk.com/?search={prepairedArtist.replace(' ', '%20')}%20-%20{prepairedName.replace(' ', '%20')}",
            'YouTube': f"https://www.youtube.com/results?search_query={prepairedArtist.replace(' ', '+')}+-+{prepairedName.replace(' ', '+')}",
        }

        self.setUI()

    def setUI(self):
        self.mainlayout = QHBoxLayout()

        self.layoutnames = QVBoxLayout()
        self.layoutnames.setAlignment(QtCore.Qt.AlignLeft)
        self.layoutnames.setObjectName('layoutnames')
        self.labelname = QLabel()
        self.labelname.setText(self.track.name)
        self.labelname.setObjectName('labelname')
        self.labelartist = QLabel()
        self.labelartist.setText(self.track.artist)
        self.labelartist.setObjectName('labelartist')
        self.labelplaylists = QLabel()
        self.labelplaylists.setText(', '.join(self.track.playlists))
        self.labelplaylists.setObjectName('labelplaylists')
        self.layoutnames.addWidget(self.labelname)
        self.layoutnames.addWidget(self.labelartist)
        self.layoutnames.addWidget(self.labelplaylists)
        
        self.layoutButtonsInfo = QVBoxLayout()
        self.layoutButtonsInfo.setAlignment(QtCore.Qt.AlignRight)
        self.layoutButtonsInfo.setObjectName('layoutbuttonsinfo')
        self.labeltime = QLabel()
        self.labeltime.setText(self.track.time)
        self.labeltime.setObjectName('labeltime')
        self.checkout = QCheckBox()
        self.checkout.setObjectName("checkbox")
        self.checkout.setToolTip('downloaded')
        if self.track.downloaded:
            self.checkout.setChecked(True)   
        self.checkout.stateChanged.connect(self.changeCheckStatus)    
        self.labelinfo = QLabel()
        self.labelinfo.setText(f'Добавлен: {self.track.date}')
        self.labelinfo.setObjectName('labelinfo')
        self.layoutButtonsInfo.addWidget(self.labeltime)
        self.layoutButtonsInfo.addWidget(self.checkout)
        self.layoutButtonsInfo.addWidget(self.labelinfo)

        self.mainlayout.addLayout(self.layoutnames)
        self.mainlayout.addStretch(1)
        self.mainlayout.addLayout(self.layoutButtonsInfo)
        self.setLayout(self.mainlayout)

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setObjectName("trackwidget")
        self.setToolTip(f'{self.track.get_name()}\n(double click to copy to clipboard)')
        self.installEventFilter(self)

        self.setAcceptDrops(True)

        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        for key in self.links.keys():
            action = QAction()
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
        if state == Qt.Checked:
            work_xml.changeStatus(self.track.track_id, True)
        else:
            work_xml.changeStatus(self.track.track_id, False)
        

class Ui_Form(object):
    def createWidget(self, Form, track):
        widget = TrackWidget(Form, track)
        return widget

    def setupUi(self, Form):
        Form.setWindowTitle("Your Spoty")
        Form.setObjectName("form")
        Form.resize(600, 800)
        Form.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        tracks = work_xml.Load_list()

        self.layout = QVBoxLayout()
        for i, track in enumerate(tracks):
            self.layout.addWidget(self.createWidget(Form, track))

        self.layoutTracks = QHBoxLayout()
        self.tracks = QWidget()
        self.tracks.setObjectName('listwidget')
        self.tracks.setLayout(self.layout)
        self.layoutTracks.addWidget(self.tracks)

        self.scrollArea = QScrollArea(Form)
        self.scrollArea.setGeometry(QtCore.QRect(0, 0, Form.size().width(), Form.size().height() - 40))
        self.scrollArea.setLayout(self.layoutTracks)
        self.scrollArea.setObjectName("scrollarea")

class Main(QtWidgets.QWidget, Ui_Form):
    resized = QtCore.pyqtSignal() 
    def __init__(self, parent=None):
        super(Main, self).__init__(parent) 
        self.setupUi(self)
        self.resized.connect(self.sizeChanged)
        
    def resizeEvent(self, event):
        self.resized.emit()
        return super(Main, self).resizeEvent(event)

    def sizeChanged(self):
        self.scrollArea.setGeometry(QtCore.QRect(0, 0, self.size().width(), self.size().height() - 40))           

if __name__ == '__main__':
    styleWidget = '''
            #layoutbuttonsinfo, #layoutnames {
                width: 50%;
                display: flex;
            }
            #scrollarea, #trackwidget, #listwidget {
                background-color: #ffffff;
                border-width: 0;
                padding: 0;
                margin: 0;
            }
            #trackwidget:hover {
                background-color: #efefef;
            }
            #checkbox {
                border-radius: 10px;
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
    ex  = Main()
    ex.show()
    sys.exit(app.exec_()) 



# tracks = loadTracks()



