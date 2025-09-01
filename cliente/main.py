from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class MainApp(QMainWindow):
    def __init__(self, parent=None, *args):
        super(MainApp, self).__init__(parent=parent)

        self.setMinimumSize(500, 300)
        #self.setMaximumSize(700, 500)
        #self.setFixedSize(500, 300)
        self.setWindowTitle("Nestlink App")

        label = QLabel("Bienvenido a Nestlink", self)

app = QApplication([])
window = MainApp()
window.show()
app.exec_()
