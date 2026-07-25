from os import sys 
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(500,500,500,500)
        self.line_edit = QLineEdit(self)
        self.button = QPushButton("Submit",self)
        self.initUI()

    def initUI(self):
        self.line_edit.setGeometry(10, 10, 200, 35)
        self.line_edit.setStyleSheet("font-size: 25px; font-family: arial;")
        self.button.setGeometry(210, 10, 100, 35)
        self.button.setStyleSheet("font-size: 25px; font-family: arial;")
        self.line_edit.setPlaceholderText("Enter your name.")

        self.button.clicked.connect(self.button_clicked)

    def button_clicked(self):
        name = self.line_edit.text()
        print(f"hello!, {name}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())