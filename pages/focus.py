# from PyQt5.QtWidgets import (
#     QWidget,
#     QVBoxLayout,
#     QHBoxLayout,
#     QLabel
# )
# from PyQt5.QtCore import Qt
# from widgets.timer_dial import TimerDial
# from PyQt5.QtGui import QColor

# class focuspage(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setObjectName("focusPage")

#         #---- Main vertical layout ----
#         main_layout = QVBoxLayout(self)
#         main_layout.setContentsMargins(12, 8, 12, 8)
#         main_layout.setSpacing(20)
#         header = QVBoxLayout()

#         eyebrow = QLabel("YOUR PRODUCTIVITY")
#         eyebrow.setObjectName("eyebrow")

#         title = QLabel("Focus")
#         title.setObjectName("pageTitle")
#         subtitle = QLabel("One thing at a time. Make it count.")
#         subtitle.setObjectName("mutedText")
#         header.addWidget(eyebrow)
#         header.addWidget(title)
#         header.addWidget(subtitle)
#         main_layout.addLayout(header)

#         #---- Timer area -----
#         timer_area = QHBoxLayout()
#         timer_area.setSpacing(20)

#         self.timer_dial = TimerDial()
#         self.timer_dial.setObjectName("timerDial")

#         self.timer_display = QLabel("25:00")
#         self.timer_display.setObjectName("timerDisplay")
#         self.timer_display.setAlignment(Qt.AlignCenter)

#         timer_area.addWidget(self.timer_dial, 2)
#         timer_area.addWidget(self.timer_display, 1)

#         main_layout.addLayout(timer_area)

#         main_layout.addStretch()

import os
import math
import struct
import wave
import tempfile

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QButtonGroup,
)
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtMultimedia import QSoundEffect
from widgets.timer_dial import TimerDial

# One place that describes every mode. Change minutes here (use 1 to test fast).
MODES = {
    "focus": {"label": "Focus",       "minutes": 25, "color": "#8B9CF6",
              "running": "Focus in progress", "ready": "Ready to focus"},
    "short": {"label": "Short Break", "minutes": 5,  "color": "#6FCF97",
              "running": "Break in progress", "ready": "Take a breather"},
    "long":  {"label": "Long Break",  "minutes": 15, "color": "#F2B66D",
              "running": "Rest in progress",  "ready": "You earned it"},
}


def make_chime(path):
    """Write a short 3-note chime (E5, G5, C6) as a WAV file."""
    rate = 44100
    notes = [(659.25, 0.30), (783.99, 0.30), (1046.50, 0.60)]  # (Hz, seconds)
    frames = bytearray()
    for freq, duration in notes:
        count = int(rate * duration)
        for i in range(count):
            t = i / rate
            fade = math.exp(-4 * t / duration) * min(1, i / 200)  # decays, no click at start
            sample = math.sin(2 * math.pi * freq * t) * fade
            frames += struct.pack("<h", int(sample * 0.6 * 32767))
    with wave.open(path, "wb") as f:
        f.setnchannels(1)       # mono
        f.setsampwidth(2)       # 16-bit
        f.setframerate(rate)
        f.writeframes(bytes(frames))


class focuspage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("focusPage")

        # ---- state ----
        self.mode = "focus"
        self.total_seconds = 0
        self.remaining = 0
        self.sessions = 0                       # completed focus sessions

        # ---- the clock: fires tick() once per second ----
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.tick)

        # ---- alarm sound ----
        chime_path = os.path.join(tempfile.gettempdir(), "dayos_chime.wav")
        if not os.path.exists(chime_path):
            make_chime(chime_path)
        self.alarm = QSoundEffect(self)
        self.alarm.setSource(QUrl.fromLocalFile(chime_path))
        self.alarm.setVolume(0.8)      # 0.0 to 1.0
        self.alarm.setLoopCount(2)     # plays twice

        # ---- layout ----
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(20)

        # header
        header = QVBoxLayout()
        eyebrow = QLabel("YOUR PRODUCTIVITY")
        eyebrow.setObjectName("eyebrow")
        title = QLabel("Focus")
        title.setObjectName("pageTitle")
        subtitle = QLabel("One thing at a time. Make it count.")
        subtitle.setObjectName("mutedText")
        header.addWidget(eyebrow)
        header.addWidget(title)
        header.addWidget(subtitle)
        main_layout.addLayout(header)

        # mode tabs (Focus / Short Break / Long Break)
        mode_row = QHBoxLayout()
        mode_row.setSpacing(10)
        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)
        self.mode_buttons = {}
        for key, info in MODES.items():
            btn = QPushButton(info["label"])
            btn.setObjectName("modeButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _checked, k=key: self.set_mode(k))
            self.mode_group.addButton(btn)
            mode_row.addWidget(btn)
            self.mode_buttons[key] = btn
        main_layout.addLayout(mode_row)

        # dial
        self.timer_dial = TimerDial()
        self.timer_dial.setObjectName("timerDial")
        main_layout.addWidget(self.timer_dial, 1)

        # controls
        controls = QHBoxLayout()
        controls.setSpacing(12)
        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("primaryButton")
        self.start_button.setCursor(Qt.PointingHandCursor)
        self.start_button.clicked.connect(self.toggle_timer)

        self.reset_button = QPushButton("Reset")
        self.reset_button.setObjectName("secondaryButton")
        self.reset_button.setCursor(Qt.PointingHandCursor)
        self.reset_button.clicked.connect(self.reset_timer)

        controls.addStretch()
        controls.addWidget(self.start_button)
        controls.addWidget(self.reset_button)
        controls.addStretch()
        main_layout.addLayout(controls)

        # session counter
        self.session_label = QLabel()
        self.session_label.setObjectName("mutedText")
        self.session_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.session_label)

        main_layout.addStretch()

        self.set_mode("focus")

    # ------------------------------------------------------------------
    def set_mode(self, mode):
        """Switch to a mode and load its full time (stops the clock)."""
        self.timer.stop()
        self.mode = mode
        self.total_seconds = MODES[mode]["minutes"] * 60
        self.remaining = self.total_seconds
        self.mode_buttons[mode].setChecked(True)   # keeps tabs in sync on auto-switch
        self.timer_dial.set_color(MODES[mode]["color"])
        self.refresh()

    def toggle_timer(self):
        if self.timer.isActive():
            self.timer.stop()                      # pause
        else:
            self.timer.start()                     # start / resume
        self.refresh()

    def reset_timer(self):
        self.timer.stop()
        self.alarm.stop()                          # silence the chime if it's playing
        self.remaining = self.total_seconds
        self.refresh()

    def tick(self):
        self.remaining -= 1
        if self.remaining <= 0:
            self.finish()
        else:
            self.refresh()

    def finish(self):
        """Timer hit zero: ring, count the session and move to the next mode."""
        self.alarm.play()
        if self.mode == "focus":
            self.sessions += 1
            next_mode = "long" if self.sessions % 4 == 0 else "short"
        else:
            next_mode = "focus"
        self.set_mode(next_mode)

    def refresh(self):
        """Push the current state to the dial and the buttons."""
        minutes, seconds = divmod(self.remaining, 60)
        info = MODES[self.mode]

        if self.timer.isActive():
            status = info["running"]
        elif self.remaining < self.total_seconds:
            status = "Paused"
        else:
            status = info["ready"]

        progress = self.remaining / self.total_seconds
        self.timer_dial.set_state(f"{minutes:02d}:{seconds:02d}", status, progress)

        self.start_button.setText("Pause" if self.timer.isActive() else "Start")
        self.session_label.setText(f"Sessions completed: {self.sessions}")