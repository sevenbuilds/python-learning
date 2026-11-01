from PyQt5.QtCore import QTimer, QDateTime, Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGridLayout
    )
from widgets.infocard import InfoCard
from widgets.helpers import make_scroll

class homepage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("homepage")

        # The whole page scrolls, so small windows never squash the cards.
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll, vbox = make_scroll()
        outer.addWidget(scroll)
        vbox.setContentsMargins(12, 8, 12, 8)
        vbox.setSpacing(20)

        top = QHBoxLayout()
        heading_box = QVBoxLayout()
        eyebrow = QLabel("YOUR PERSONAL SPACE")
        eyebrow.setObjectName("eyebrow")
        self.greeting = QLabel("Good evening.")
        self.greeting.setObjectName("pageTitle")
        subtitle = QLabel("A calmer place to organize your day.")
        subtitle.setObjectName("mutedText")
        heading_box.addWidget(eyebrow)
        heading_box.addWidget(self.greeting)
        heading_box.addWidget(subtitle)

        self.clock = QLabel()
        self.clock.setObjectName("clock")
        # here | means or
        self.clock.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        top.addLayout(heading_box)
        top.addStretch()
        top.addWidget(self.clock)
        vbox.addLayout(top)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        # 1000 milisecond = 1 second
        self.timer.start(1000)
        self.update_clock()

        section = QLabel("OVERVIEW")
        section.setObjectName("sectionTitle")
        vbox.addWidget(section)

        self.focus_card = InfoCard(
            "FOCUS",
            "Ready when you are",
            "A space for your next focused session.",
            "Start a session →"
        )
        self.weather_card = InfoCard(
            "WEATHER",
            "Loading…",
            "Fetching your local forecast.",
            "View forecast →"
        )
        self.calendar_card = InfoCard(
            "UP NEXT",
            "Your schedule",
            "Calendar events and reminders will appear here.",
            "Open calendar →"
        )
        self.notes_card = InfoCard(
            "QUICK NOTES",
            "Nothing to capture yet",
            "Note down an idea before it disappears.",
            "Create a note →"
        )
        self.tasks_card = InfoCard(
            "TO-DO",
            "No tasks yet",
            "Capture what you need to get done.",
            "Open tasks →"
        )

        # 6 equal columns: top row = 3 cards (2 columns each),
        #                  bottom row = 2 cards (3 columns each)
        grid = QGridLayout()
        grid.setSpacing(14)
        for column in range(6):
            grid.setColumnStretch(column, 1)
        grid.addWidget(self.focus_card,    0, 0, 1, 2)
        grid.addWidget(self.weather_card,  0, 2, 1, 2)
        grid.addWidget(self.calendar_card, 0, 4, 1, 2)
        grid.addWidget(self.notes_card,    1, 0, 1, 3)
        grid.addWidget(self.tasks_card,    1, 3, 1, 3)
        vbox.addLayout(grid)
        vbox.addStretch()

    def update_clock(self):
        now = QDateTime.currentDateTime()
        self.clock.setText(
            now.toString("hh:mm") + "\n" + now.toString("dddd, d MMMM")
        )

        hour = now.time().hour()
        if hour >= 5 and hour < 12:
            greeting = "Good morning."
        elif hour >= 12 and hour < 17:
            greeting = "Good afternoon."
        elif hour >= 17 and hour < 22:
            greeting = "Good evening."
        else:
            greeting = "Welcome back."

        self.greeting.setText(greeting)