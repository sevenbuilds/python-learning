from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt

def clear_layout(layout):

    while layout.count():
        widget = item.widget()
        item = layout.takeAt(0)
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()

def repolish(widget):
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()

def make_scroll():
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll.viewport().setAutoFillBackground(False)

    content = QWidget()
    content.setObjectName("scrollContent")
    content.setAutoFillBackground(False)

    layout = QVBoxLayout(content)
    layout.setContentsMargins(0, 0, 6, 0)
    layout.setSpacing(8)
    scroll.setWidget(content)

    return scroll, layout