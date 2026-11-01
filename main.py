import sys
from datetime import datetime, date
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QStackedWidget,
    QHBoxLayout
)
# --- importing modules ----
from PyQt5.QtCore import QTimer
from pages.home import homepage
from pages.focus import focuspage
from pages.weather import weatherpage
from pages.notes import notespage
from pages.calendar_page import calendarpage
from pages.tasks import taskspage
from widgets.sidebar import Sidebar
from widgets.toast import ToastHost
from services.planner_data import PlannerData
from services.reminders import ReminderService
from services.sound import play_reminder_sound
from styles.theme import APP_STYLE

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.Name = "DayOS"
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        width = int(screen_geometry.width() * 0.85)
        height = int(screen_geometry.height() * 0.85) # only cover 85 percent of the screen

        self.resize(width, height)
        self.setMinimumSize(600, 400)
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.Name)
        central = QWidget()
        central.setObjectName("appRoot")
        layout = QHBoxLayout(central)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)
        self.sidebar = Sidebar()
        self.data = PlannerData()

        #---- create application pages -----
        self.home_page = homepage()
        self.focus_page = focuspage()
        self.weather_page = weatherpage()
        self.calendar_page = calendarpage(self.data)
        self.tasks_page = taskspage(self.data)
        self.notes_page = notespage()

        #--- adding page to stacked widgets ---
        self.pages = QStackedWidget()

        self.pages.addWidget(self.home_page)
        self.pages.addWidget(self.focus_page)
        self.pages.addWidget(self.weather_page)
        self.pages.addWidget(self.calendar_page)
        self.pages.addWidget(self.tasks_page)
        self.pages.addWidget(self.notes_page)

        layout.addWidget(self.sidebar)
        layout.addWidget(self.pages, 1)

        self.setCentralWidget(central)

        #---- events ----
        self.sidebar.buttons[0].clicked.connect(self.show_home)
        self.sidebar.buttons[1].clicked.connect(self.show_focus)
        self.sidebar.buttons[2].clicked.connect(self.show_weather)
        self.sidebar.buttons[3].clicked.connect(self.show_calendar)
        self.sidebar.buttons[4].clicked.connect(self.show_tasks)
        self.sidebar.buttons[5].clicked.connect(self.show_notes)

        self.home_page.focus_card.clicked.connect(self.show_focus)
        self.home_page.weather_card.clicked.connect(self.show_weather)
        self.home_page.notes_card.clicked.connect(self.show_notes)
        self.home_page.calendar_card.clicked.connect(self.show_calendar)
        self.home_page.tasks_card.clicked.connect(self.show_tasks)

        # ---- updating home pages -----
        self.weather_page.summary_changed.connect(
            self.home_page.weather_card.set_content
        )
        self.notes_page.summary_changed.connect(
            self.home_page.notes_card.set_content
        )

        self.notes_page.emit_summary()
        self.data.changed.connect(self.update_planner_cards)
        #every 30000ms = 30s we update the info
        self.summary_timer = QTimer(self)
        self.summary_timer.timeout.connect(self.update_planner_cards)
        self.summary_timer.start(30000)
        self.update_planner_cards()
        
        self.toasts = ToastHost(central)
        self.reminders = ReminderService(self.data)
        self.reminders.fired.connect(self.on_reminder)

    #----build page navigation -----
    def show_home(self):
        self.pages.setCurrentWidget(self.home_page)
        self.sidebar.set_active(0)

    def show_focus(self):
        self.pages.setCurrentWidget(self.focus_page)
        self.sidebar.set_active(1)

    def show_weather(self):
        self.pages.setCurrentWidget(self.weather_page)
        self.sidebar.set_active(2)

    def show_calendar(self):
        self.pages.setCurrentWidget(self.calendar_page)
        self.sidebar.set_active(3)

    def show_tasks(self):
        self.pages.setCurrentWidget(self.tasks_page)
        self.sidebar.set_active(4)

    def show_notes(self):
        self.pages.setCurrentWidget(self.notes_page)
        self.sidebar.set_active(5)

    def closeEvent(self, event):
        self.notes_page.flush()
        super().closeEvent(event)

    def update_planner_cards(self):
        title, text = self.data.next_up(datetime.now())
        self.home_page.calendar_card.set_content(title, text)
        title, text = self.data.tasks_summary(date.today())
        self.home_page.tasks_card.set_content(title, text)
    
    def on_reminder(self, title, body):
        self.toasts.show_toast(title, body)
        play_reminder_sound()
        QApplication.alert(self, 0)
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
