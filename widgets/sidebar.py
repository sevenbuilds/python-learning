from PyQt5.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSpacerItem,
    QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

class Sidebar(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(205)
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(16, 22, 16, 18)
        vbox.setSpacing(10)

        brand = QLabel("DayOS")
        brand.setObjectName("brand")
        vbox.addWidget(brand)
        sidebarCaption = QLabel("PERSONAL WORKSPACE")
        sidebarCaption.setObjectName("sidebarCaption")
        vbox.addWidget(sidebarCaption)
        vbox.addSpacing(28)

        self.buttons = []
        options = ["⌂   Home", "◷   Focus", "☼   Weather", "▤   Calendar", "☑   Tasks", "✎   Notes"]
        for name in options:
            button = QPushButton(name)
            button.setObjectName("navigationButton")
            button.setCursor(QCursor(Qt.PointingHandCursor))
            vbox.addWidget(button)
            self.buttons.append(button)

        vbox.addItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        settings = QPushButton("⚙   Settings")
        settings.setObjectName("navigationButton")
        vbox.addWidget(settings)

        self.set_active(0)


    def set_active(self, index):
        for i, button in enumerate(self.buttons):
            button.setProperty("active", i == index)
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()