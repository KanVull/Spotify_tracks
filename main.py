from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel, QCheckBox, QPushButton
from PyQt5.Qt import *
from tinytag import TinyTag

import os
import sys
import pyperclip
import work_xml

class TrackWidget(QWidget):
    def __init__(self, Form, track, index, parent=None):
        QWidget.__init__(self, parent=parent)
        self.widget = QWidget(Form)

        self.track = track
        self.links = {
            'KissVK': f"https://kissvk.com/?search={self.track.artist.lower().replace(' ', '%20')}%20-%20{self.track.name.lower().replace(' ', '%20')}",
            'YouTube': f"https://www.youtube.com/results?search_query={self.track.artist.lower().replace(' ', '+')}+{self.track.name.lower().replace(' ', '+')}",
        }
        self.index = index

        self.setUI()

    def setUI(self):
        # self.setGeometry(445, 50)
        self.mainlayout = QHBoxLayout(self)

        self.layoutnames = QVBoxLayout(self)
        self.labelname = QLabel(self)
        self.labelname.setText(self.track.name)
        self.labelartist = QLabel(self)
        self.labelartist.setText(self.track.artist)
        self.labelplaylists = QLabel(self)
        self.labelplaylists.setText(''.join(self.track.playlists))
        self.layoutnames.addWidget(self.labelname)
        self.layoutnames.addWidget(self.labelartist)
        self.layoutnames.addWidget(self.labelplaylists)
        
        self.layoutButtonsInfo = QVBoxLayout(self)
        self.labeltime = QLabel(self)
        self.labeltime.setText(self.track.time)

        self.layoutbutton = QHBoxLayout(self)
        self.downloadbutton = QPushButton(self)
        self.checkout = QCheckBox(self)
        if self.track.downloaded:
            self.checkout.setChecked(True)   
        self.checkout.stateChanged.connect(self.changeCheckStatus)    
        self.layoutbutton.addWidget(self.downloadbutton)
        self.layoutbutton.addWidget(self.checkout)

        self.labelinfo = QLabel(self)
        self.labelinfo.setText(f'Добавлен: {self.track.date}')
        self.layoutButtonsInfo.addWidget(self.labeltime)
        self.layoutButtonsInfo.addLayout(self.layoutbutton)
        self.layoutButtonsInfo.addWidget(self.labelinfo)

        self.mainlayout.addLayout(self.layoutnames)
        self.mainlayout.addLayout(self.layoutButtonsInfo)
        self.widget.setLayout(self.mainlayout)

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setObjectName("trackWidget")
        self.installEventFilter(self)

        self.setAcceptDrops(True)

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
            # os.rename(path[1:], new_path)

            # tag = TinyTag.get(new_path)
            tag = TinyTag.get(path[1:])
            print(tag.name)


    def eventFilter(self, obj, event):
        if obj == self and event.type() == QtCore.QEvent.MouseButtonPress:
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
    def createWidget(self, Form, track, index):
        widget = TrackWidget(Form, track, index)
        widget.setUI()
        return widget

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setFixedSize(463, 600)
        Form.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        # Form.setStyleSheet('background-color: #ffffff;')

        tracks = work_xml.Load_list()

        self.layout = QVBoxLayout(Form)
        for i, track in enumerate(tracks):
            ## Generate widget
            if i > 5:
                break
            self.layout.addWidget(self.createWidget(Form, track, i))

        self.w = QWidget(Form)
        self.w.setObjectName('listLayout')
        self.w.setLayout(self.layout)

        self.scrollArea = QScrollArea(Form)
        self.scrollArea.setGeometry(QtCore.QRect(0, 0, Form.size().width(), Form.size().height() - 40))
        self.scrollArea.setWidget(self.w)
        self.scrollArea.setObjectName("scrollArea")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle("Your Spoty")
        # self.pushButton.setText("PushButton")

class Main(QtWidgets.QWidget, Ui_Form): 
    def __init__(self, parent=None):
        super(Main, self).__init__(parent) 
        self.setupUi(self)   

if __name__ == '__main__':
    styleWidget = '''
            #scrollArea, #trackWidget, #listLayout {
                background-color: #ffffff;
            }
            #trackWidget:hover {
                background-color: #efefef;
            }
        '''
    app = QApplication(sys.argv)
    app.setStyleSheet(styleWidget)
    ex  = Main()
    ex.show()
    sys.exit(app.exec_()) 



# tracks = loadTracks()



