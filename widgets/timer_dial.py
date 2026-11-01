# from PyQt5.QtWidgets import QWidget
# from PyQt5.QtCore import Qt
# from PyQt5.QtGui import QPainter, QPen, QColor

# class TimerDial(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setMinimumSize(280, 280)
#         self.progress = 0.65
#         self.progress_color = QColor("#8B9CF6")

#     def paintEvent(self, event):
#         painter = QPainter(self)
#         painter.setRenderHint(QPainter.Antialiasing)

#         center_x = self.width() / 2
#         center_y = self.height() / 2

#         #---- Circle -----
#         radius = min(self.width(), self.height()) * 0.38
#         background_pen = QPen(QColor("#303744"), 12)
#         background_pen.setCapStyle(Qt.RoundCap)

#         painter.setPen(background_pen)
#         painter.drawEllipse(
#             int(center_x - radius),
#             int(center_y - radius),
#             int(radius * 2),
#             int(radius * 2)
#         )
#         progress_pen = QPen(self.progress_color, 12)
#         progress_pen.setCapStyle(Qt.RoundCap)

#         painter.setPen(progress_pen)

#         start_angle = 90 * 16
#         span_angle = -self.progress * 360 * 16

#         painter.drawArc(
#             int(center_x - radius),
#             int(center_y - radius),
#             int(radius * 2),
#             int(radius * 2),
#             start_angle,
#             int(span_angle)
#         )
#         painter.end()

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QColor, QFont


class TimerDial(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(320, 320)
        self.progress = 1.0                      # 1.0 = full ring, 0.0 = empty
        self.progress_color = QColor("#8B9CF6")
        self.time_text = "25:00"
        self.status_text = "Ready to focus"

    # ---- setters: the focus page calls these, then we repaint ----
    def set_state(self, time_text, status_text, progress):
        self.time_text = time_text
        self.status_text = status_text
        self.progress = progress
        self.update()                            # schedules paintEvent

    def set_color(self, hex_color):
        self.progress_color = QColor(hex_color)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        cx = self.width() / 2
        cy = self.height() / 2
        radius = min(self.width(), self.height()) * 0.38
        ring = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)

        # ---- background track ----
        track_pen = QPen(QColor("#303744"), 12)
        track_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(track_pen)
        painter.drawEllipse(ring)

        # ---- progress arc (starts at 12 o'clock, shrinks clockwise) ----
        if self.progress > 0:
            progress_pen = QPen(self.progress_color, 12)
            progress_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(progress_pen)
            painter.drawArc(ring, 90 * 16, int(-self.progress * 360 * 16))

        # ---- big time text ----
        painter.setPen(QColor("#f4f6fb"))
        time_font = QFont("Segoe UI")
        time_font.setPixelSize(int(radius * 0.42))
        time_font.setWeight(QFont.DemiBold)
        painter.setFont(time_font)
        painter.drawText(
            QRectF(ring.left(), cy - radius * 0.45, ring.width(), radius * 0.7),
            Qt.AlignCenter,
            self.time_text,
        )

        # ---- small status text ----
        painter.setPen(QColor("#929db2"))
        status_font = QFont("Segoe UI")
        status_font.setPixelSize(int(radius * 0.11))
        painter.setFont(status_font)
        painter.drawText(
            QRectF(ring.left(), cy + radius * 0.3, ring.width(), radius * 0.3),
            Qt.AlignCenter,
            self.status_text,
        )
        painter.end()