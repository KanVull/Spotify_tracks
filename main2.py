from PyQt5 import QtCore, QtGui, QtWidgets
import time

class MyProccess(QtCore.QThread):

    newProgress = QtCore.pyqtSignal(str)

    def __init__(self,i):
        super(MyProccess,self).__init__()
        self.id = i

    def run(self):
        for j in range(10):
            self.newProgress.emit('task %d at %d%%' % (self.id,j*10))
            time.sleep(0.2)            


class MySplash(QtWidgets.QSplashScreen):

    def __init__(self, mw):
        super(MySplash,self).__init__()
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)
        self.text = QtWidgets.QLabel(self)
        layout.addWidget(self.text) 
        self.setGeometry(300,300,100,0)          

        self.task1 = MyProccess(1)
        self.task2 = MyProccess(2)
        self.task3 = MyProccess(3)

        self.task1.newProgress.connect(self.showProgress)
        self.task2.newProgress.connect(self.showProgress)
        self.task3.newProgress.connect(self.showProgress)

        self.task1.finished.connect(self.task2.start)
        self.task2.finished.connect(self.task3.start)
        self.task3.finished.connect(mw.show)
        self.task3.finished.connect(self.hide)

    def showProgress(self,msg):
        self.text.setText(msg)

    def event(self,ev):
        if type(ev) == QtGui.QShowEvent:
            self.task1.start()
        return super(MySplash,self).event(ev)

app = QtWidgets.QApplication([])

mw = QtWidgets.QMainWindow()

cw = QtWidgets.QWidget()
l = QtWidgets.QHBoxLayout()
cw.setLayout(l)
welcome = QtWidgets.QLabel()
welcome.setText('Welcome back!')
l.addWidget(welcome)

mw.setCentralWidget(cw)
mw.setGeometry(200,200,300,300)


w = MySplash(mw)
w.show()

app.exec_()