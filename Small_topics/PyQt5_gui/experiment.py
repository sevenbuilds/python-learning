from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QIcon, QPixmap
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(r"python_learning\Small_topics\PyQt5_gui\nanami.jpg"))
        self.setGeometry(0,0,500,500)
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        label = QLabel("nanami",self)

        label.setPixmap(QPixmap(r"python_learning\Small_topics\PyQt5_gui\nanami.jpg"))

        vbox = QVBoxLayout()


if __name__ == "__main__":
    apps = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(apps.exec_())