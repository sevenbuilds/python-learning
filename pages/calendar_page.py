from datetime import date, timedelta
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QSizePolicy, QDialog, QMessageBox,
)
from PyQt5.QtCore import Qt, pyqtSignal
from widgets.helpers import clear_layout, make_scroll, repolish
from widgets.planner_dialogs import EventDialog, TaskDialog

class DayCell(QPushButton):
    def __init__(self):
        super().__init__()
        self.setObjectName("dayCell")
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.date = None

    def configure(self, day, count, today, selected, other_month):
        self.date = day
        dots = "●" * min(count, 3) if count else " "
        self.setText(f"{day.day}\n{dots}")
        self.setProperty("today", day == today)
        self.setProperty("selected", day == selected)
        self.setProperty("otherMonth", other_month)
        repolish(self)

class ScheduleRow(QFrame):
    """One line in the selected day's schedule (an event or a task)."""
    edit_requested = pyqtSignal(str, str)      # kind, id
    delete_requested = pyqtSignal(str, str)
    toggled = pyqtSignal(str)

    def __init__(self, item):
        super().__init__()
        self.setObjectName("scheduleRow")
        self.kind = item["kind"]
        self.item_id = item["id"]
        row = QHBoxLayout(self)
        row.setContentsMargins(12, 10, 8, 10)
        row.setSpacing(10)
        if self.kind == "event":
            bar = QFrame()
            bar.setFixedWidth(4)
            bar.setStyleSheet(f"background-color: {item['color']}; border-radius: 2px;")
            row.addWidget(bar)
            time_text = item["start"] + (f" – {item['end']}" if item["end"] else "")
        else:
            check = QPushButton("✓" if item["done"] else "")
            check.setObjectName("checkButton")
            check.setCheckable(True)
            check.setChecked(item["done"])
            check.setCursor(Qt.PointingHandCursor)
            check.clicked.connect(lambda: self.toggled.emit(self.item_id))
            row.addWidget(check)
            time_text = item["start"] or "Anytime"

        time_label = QLabel(time_text)
        time_label.setObjectName("scheduleTime")
        time_label.setFixedWidth(104)
        title = QLabel(item["title"])
        title.setObjectName("scheduleTitle")
        title.setWordWrap(True)
        title.setProperty("done", bool(item.get("done")))

        row.addWidget(time_label)
        row.addWidget(title, 1)

        badges = ""
        if item["remind"] >= 0:
            badges += "🔔"
        if item["repeat"] != "none":
            badges += " ↻"
        if badges:
            badge = QLabel(badges)
            badge.setObjectName("scheduleBadge")
            row.addWidget(badge)

        edit = QPushButton("✎")
        edit.setObjectName("iconButton")
        edit.setCursor(Qt.PointingHandCursor)
        edit.clicked.connect(lambda: self.edit_requested.emit(self.kind, self.item_id))
        remove = QPushButton("✕")
        remove.setObjectName("iconButton")
        remove.setCursor(Qt.PointingHandCursor)
        remove.clicked.connect(lambda: self.delete_requested.emit(self.kind, self.item_id))
        row.addWidget(edit)
        row.addWidget(remove)

class calendarpage(QWidget):
    def __init__(self, data):
        super().__init__()
        self.setObjectName("calendarPage")
        self.data = data
        self.selected = date.today()
        self.month = self.selected.replace(day=1)       # first day of the month on screen

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(20)

        # ---- header ----
        top = QHBoxLayout()
        heading = QVBoxLayout()
        eyebrow = QLabel("YOUR SCHEDULE")
        eyebrow.setObjectName("eyebrow")
        title = QLabel("Calendar")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Plan your days and never miss a thing.")
        subtitle.setObjectName("mutedText")
        heading.addWidget(eyebrow)
        heading.addWidget(title)
        heading.addWidget(subtitle)
        add_button = QPushButton("+  New event")
        add_button.setObjectName("primaryButton")
        add_button.setCursor(Qt.PointingHandCursor)
        add_button.clicked.connect(self.add_event)
        top.addLayout(heading)
        top.addStretch()
        top.addWidget(add_button, 0, Qt.AlignTop)
        main_layout.addLayout(top)

        body = QHBoxLayout()
        body.setSpacing(16)

        # ---- left: month grid ----
        left = QFrame()
        left.setObjectName("calendarPanel")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(18, 16, 18, 18)
        left_layout.setSpacing(12)

        nav = QHBoxLayout()
        prev_button = QPushButton("‹")
        next_button = QPushButton("›")
        today_button = QPushButton("Today")
        for button in (prev_button, next_button, today_button):
            button.setObjectName("smallButton")
            button.setCursor(Qt.PointingHandCursor)
        prev_button.clicked.connect(self.previous_month)
        next_button.clicked.connect(self.next_month)
        today_button.clicked.connect(self.go_to_today)
        self.month_label = QLabel()
        self.month_label.setObjectName("monthLabel")
        nav.addWidget(self.month_label)
        nav.addStretch()
        nav.addWidget(prev_button)
        nav.addWidget(today_button)
        nav.addWidget(next_button)
        left_layout.addLayout(nav)
        grid = QGridLayout()
        grid.setSpacing(6)
        for col, name in enumerate(["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]):
            label = QLabel(name)
            label.setObjectName("weekdayLabel")
            label.setAlignment(Qt.AlignCenter)
            grid.addWidget(label, 0, col)
            grid.setColumnStretch(col, 1)
        self.cells = []
        for i in range(42):                              # 6 weeks x 7 days
            cell = DayCell()
            cell.clicked.connect(lambda _checked, c=cell: self.select_day(c.date))
            grid.addWidget(cell, 1 + i // 7, i % 7)
            self.cells.append(cell)
        for row in range(1, 7):
            grid.setRowStretch(row, 1)
        left_layout.addLayout(grid, 1)

        # ---- right: the selected day ----
        right = QFrame()
        right.setObjectName("dayPanel")
        right.setFixedWidth(360)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(18, 18, 18, 16)
        right_layout.setSpacing(6)
        self.day_title = QLabel()
        self.day_title.setObjectName("dayTitle")
        self.day_sub = QLabel()
        self.day_sub.setObjectName("mutedText")
        scroll, self.rows_layout = make_scroll()
        right_layout.addWidget(self.day_title)
        right_layout.addWidget(self.day_sub)
        right_layout.addSpacing(8)
        right_layout.addWidget(scroll, 1)
        add_here = QPushButton("+  Add to this day")
        add_here.setObjectName("secondaryButton")
        add_here.setCursor(Qt.PointingHandCursor)
        add_here.clicked.connect(self.add_event)
        right_layout.addWidget(add_here)

        body.addWidget(left, 1)
        body.addWidget(right)
        main_layout.addLayout(body, 1)

        self.data.changed.connect(self.refresh)
        self.refresh()

    def previous_month(self):
        self.shift_month(-1)
    def next_month(self):
        self.shift_month(1)
    def go_to_today(self):
        self.select_day(date.today())

    def refresh(self):
        self.refresh_grid()
        self.refresh_day()

    def refresh_grid(self):
        today = date.today()
        first = self.month
        start = first - timedelta(days=first.weekday())      # Monday on/before the 1st
        self.month_label.setText(first.strftime("%B %Y"))
        for i, cell in enumerate(self.cells):
            day = start + timedelta(days=i)
            cell.configure(day, self.data.count_on(day), today,
                           day == self.selected, day.month != first.month)

    def refresh_day(self):
        day = self.selected
        items = self.data.items_on(day)
        self.day_title.setText(f"{day:%A}, {day.day} {day:%B}")
        self.day_sub.setText(
            "Nothing planned" if not items
            else f"{len(items)} item{'s' if len(items) != 1 else ''}"
        )
        clear_layout(self.rows_layout)
        if not items:
            empty = QLabel("A free day. Add an event, a reminder or a task due today.")
            empty.setObjectName("mutedText")
            empty.setWordWrap(True)
            self.rows_layout.addWidget(empty)
        for item in items:
            row = ScheduleRow(item)
            row.edit_requested.connect(self.edit_item)
            row.delete_requested.connect(self.delete_item)
            row.toggled.connect(self.data.toggle_task)
            self.rows_layout.addWidget(row)
        self.rows_layout.addStretch()

    def shift_month(self, delta):
        if delta > 0:
            self.month = (self.month.replace(day=28) + timedelta(days=4)).replace(day=1)
        else:
            self.month = (self.month - timedelta(days=1)).replace(day=1)
        self.refresh_grid()

    def select_day(self, day):
        self.selected = day
        self.month = day.replace(day=1)
        self.refresh()

    def add_event(self):
        dialog = EventDialog(self, day=self.selected)
        if dialog.exec_() == QDialog.Accepted and dialog.result_event:
            event = dialog.result_event
            self.selected = date.fromisoformat(event["date"])
            self.month = self.selected.replace(day=1)
            self.data.upsert_event(event)

    def edit_item(self, kind, item_id):
        if kind == "event":
            event = self.data.find_event(item_id)
            if event is None:
                return
            dialog = EventDialog(self, event=event)
            if dialog.exec_() == QDialog.Accepted:
                if dialog.delete_requested:
                    self.data.delete_event(item_id)
                elif dialog.result_event:
                    self.data.upsert_event(dialog.result_event)
        else:
            task = self.data.find_task(item_id)
            if task is None:
                return
            dialog = TaskDialog(self, task=task)
            if dialog.exec_() == QDialog.Accepted:
                if dialog.delete_requested:
                    self.data.delete_task(item_id)
                elif dialog.result_task:
                    self.data.upsert_task(dialog.result_task)

    def delete_item(self, kind, item_id):
        if kind == "event":
            event = self.data.find_event(item_id)
            if event is None:
                return
            text = f"Delete “{event['title']}”?"
            if event.get("repeat", "none") != "none":
                text += " This removes every repeat of it."
            if QMessageBox.question(self, "Delete event", text) == QMessageBox.Yes:
                self.data.delete_event(item_id)
        else:
            self.data.delete_task(item_id)