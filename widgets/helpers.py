from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt


def clear_layout(layout):
    """Remove (and delete) everything inside a layout."""
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()


def repolish(widget):
    """Re-apply the stylesheet after a dynamic property changed."""
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


def make_scroll():
    """A transparent scroll area. Returns (scroll_area, layout_to_add_rows_to)."""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    content = QWidget()
    content.setObjectName("scrollContent")
    layout = QVBoxLayout(content)
    layout.setContentsMargins(0, 0, 6, 0)
    layout.setSpacing(8)
    scroll.setWidget(content)
    scroll.viewport().setAutoFillBackground(False)
    content.setAutoFillBackground(False)
    return scroll, layout