from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QCursor

class InfoCard(QFrame):
    clicked = pyqtSignal()
    def __init__(self, category, title, description, action):
        super().__init__()
        self.setObjectName("infoCard")
        self.setMinimumHeight(165)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(20, 16, 20, 16)
        vbox.setSpacing(6)
        category_label = QLabel(category)
        category_label.setObjectName("cardCategory")
        # kept as attributes so set_content() can change them later
        self.title_label = QLabel(title)
        self.title_label.setObjectName("cardTitle")
        self.title_label.setWordWrap(True)
        self.description_label = QLabel(description)
        self.description_label.setObjectName("mutedText")
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        action_label = QLabel(action)
        action_label.setObjectName("cardAction")

        # top to bottom: category, title, description, (space), action
        vbox.addWidget(category_label)
        vbox.addWidget(self.title_label)
        vbox.addWidget(self.description_label, 1)
        vbox.addWidget(action_label)

    def set_content(self, title, description):
        self.title_label.setText(title)
        self.description_label.setText(description)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)