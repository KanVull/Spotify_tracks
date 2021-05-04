from PyQt5.QtWidgets import QApplication, QWidget, QLabel

import sys
import work_xml

class TrackWidget(QWidget):

    def __init__(self, track):
        super().__init__()
        self.setMinimumSize(1, 30)

    pass

def Create_Element(track):
    pass

def loadTracks():
    return work_xml.Load_list()

def main():
    app = QApplication([])
    label = QLabel('Hello World!')
    label.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


# tracks = loadTracks()



