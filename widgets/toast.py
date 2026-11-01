from PyQt5.QtWidgets import QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QEvent, pyqtSignal

class Toast(QFrame):
    dismissed = pyqtSignal(object)
    def __init__(self, title, body):
        super().__init__()
        self.setObjectName("toast")
        self.setFixedWidth(330)
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(16, 12, 12, 14)
        vbox.setSpacing(4)

        top = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("toastTitle")
        title_label.setWordWrap(True)
        close = QPushButton("✕")
        close.setObjectName("iconButton")
        close.setCursor(Qt.PointingHandCursor)
        top.addWidget(title_label, 1)
        top.addWidget(close, 0, Qt.AlignTop)
        close.clicked.connect(self.close_toast)

        body_label = QLabel(body)
        body_label.setObjectName("mutedText")
        body_label.setWordWrap(True)
        vbox.addLayout(top)
        vbox.addWidget(body_label)

        def close_toast(self):
            self.dismissed.emit(self)

class ToastHost(QWidget):
    """Floats in the bottom-right corner of its parent and stacks notifications."""
    def __init__(self, parent):
        super().__init__(parent)
        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.setSpacing(10)
        parent.installEventFilter(self)       # so we can follow window resizes
        self.hide()

    def show_toast(self, title, body):
        toast = Toast(title, body)
        toast.dismissed.connect(self.remove_toast)
        self.vbox.addWidget(toast)
        self.show()
        self.raise_()
        self.reposition()

    def remove_toast(self, toast):
        self.vbox.removeWidget(toast)
        toast.hide()
        toast.deleteLater()
        if self.vbox.count() == 0:
            self.hide()
        else:
            self.reposition()

    def reposition(self):
        parent = self.parentWidget()
        self.adjustSize()
        self.move(parent.width() - self.width() - 24, parent.height() - self.height() - 24)

    def eventFilter(self, obj, event):
        if obj is self.parentWidget() and event.type() == QEvent.Resize and self.isVisible():
            self.reposition()
        return False