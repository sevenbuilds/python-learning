from datetime import date, datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QDateEdit,
    QTimeEdit, QComboBox, QCheckBox, QPushButton, QLabel, QMessageBox,
)
from PyQt5.QtCore import Qt, QDate, QTime
from services.planner_data import (COLORS, REMINDER_OPTIONS, REPEAT_OPTIONS, PRIORITIES, new_id)

def to_qdate(d):
    return QDate(d.year, d.month, d.day)

def fill_combo(combo, options, current):
    for label, value in options:
        combo.addItem(label, value)
    combo.setCurrentIndex(max(combo.findData(current), 0))

def make_date_edit(d):
    edit = QDateEdit(to_qdate(d))
    edit.setCalendarPopup(True)
    edit.setDisplayFormat("ddd, dd MMM yyyy")
    return edit

def make_time_edit(text):
    edit = QTimeEdit(QTime.fromString(text, "HH:mm"))
    edit.setDisplayFormat("HH:mm")
    return edit

def button_row(dialog, save_text, with_delete):
    row = QHBoxLayout()
    row.setSpacing(10)
    if with_delete:
        delete = QPushButton("Delete")
        delete.setObjectName("dangerButton")
        delete.clicked.connect(dialog.request_delete)
        row.addWidget(delete)
    row.addStretch()
    cancel = QPushButton("Cancel")
    cancel.setObjectName("secondaryButton")
    cancel.clicked.connect(dialog.reject)
    save = QPushButton(save_text)
    save.setObjectName("primaryButton")
    save.setDefault(True)
    save.clicked.connect(dialog.save)
    row.addWidget(cancel)
    row.addWidget(save)
    return row

class EventDialog(QDialog):
    """Create/edit an event. An event without an end time works as a simple reminder."""
    def __init__(self, parent, event=None, day=None):
        super().__init__(parent)
        self.setMinimumWidth(420)
        self.result_event = None
        self.delete_requested = False
        self.setWindowTitle("Edit event" if event else "New event / reminder")
        ev = event or {}
        self.event_id = ev.get("id") or new_id()

        base_day = date.fromisoformat(ev["date"]) if ev else (day or date.today())
        start_text = ev.get("start") or f"{min(datetime.now().hour + 1, 23):02d}:00"
        end_text = ev.get("end") or ""

        self.title_edit = QLineEdit(ev.get("title", ""))
        self.title_edit.setPlaceholderText("What's happening?")
        self.date_edit = make_date_edit(base_day)
        self.start_edit = make_time_edit(start_text)
        self.end_check = QCheckBox("End time")
        self.end_check.setChecked(bool(end_text))
        self.end_edit = make_time_edit(end_text or start_text)
        self.end_edit.setEnabled(bool(end_text))
        self.end_check.toggled.connect(self.end_edit.setEnabled)

        self.repeat_combo = QComboBox()
        fill_combo(self.repeat_combo, REPEAT_OPTIONS, ev.get("repeat", "none"))
        self.remind_combo = QComboBox()
        fill_combo(self.remind_combo, REMINDER_OPTIONS, ev.get("remind", 10 if not event else -1))
        self.color_combo = QComboBox()
        fill_combo(self.color_combo, COLORS, ev.get("color", COLORS[0][1]))

        end_row = QHBoxLayout()
        end_row.addWidget(self.end_check)
        end_row.addWidget(self.end_edit, 1)

        form = QFormLayout()
        form.setSpacing(12)
        
        form.addRow("Title", self.title_edit)
        form.addRow("Date", self.date_edit)
        form.addRow("Starts", self.start_edit)
        form.addRow("", end_row)
        form.addRow("Repeat", self.repeat_combo)
        form.addRow("Reminder", self.remind_combo)
        form.addRow("Color", self.color_combo)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(16)
        layout.addLayout(form)
        layout.addLayout(button_row(self, "Save", event is not None))
        self.title_edit.setFocus()

    def request_delete(self):
        self.delete_requested = True
        self.accept()

    def save(self):
        title = self.title_edit.text().strip()
        if not title:
            self.title_edit.setFocus()
            return
        start = self.start_edit.time().toString("HH:mm")
        end = self.end_edit.time().toString("HH:mm") if self.end_check.isChecked() else ""
        if end and end <= start:
            QMessageBox.warning(self, "Check the times", "The end time must be after the start time.")
            return
        self.result_event = {
            "id": self.event_id,
            "title": title,
            "date": self.date_edit.date().toPyDate().isoformat(),
            "start": start,
            "end": end,
            "repeat": self.repeat_combo.currentData(),
            "remind": self.remind_combo.currentData(),
            "color": self.color_combo.currentData(),
        }
        self.accept()

class TaskDialog(QDialog):
    def __init__(self, parent, task=None, title="", day=None):
        super().__init__(parent)
        t = task or {}
        self.setWindowTitle("Edit task" if task else "New task")
        self.setMinimumWidth(420)
        self.task_id = t.get("id") or new_id()
        self.was_done = t.get("done", False)
        self.result_task = None
        self.delete_requested = False

        due_text = t.get("due", "")
        time_text = t.get("time", "")
        due_day = date.fromisoformat(due_text) if due_text else (day or date.today())

        self.title_edit = QLineEdit(t.get("title", title))
        self.title_edit.setPlaceholderText("What needs doing?")
        self.priority_combo = QComboBox()
        fill_combo(self.priority_combo, PRIORITIES, t.get("priority", 1))

        self.due_check = QCheckBox("Due date")
        self.due_check.setChecked(bool(due_text) or day is not None)
        self.date_edit = make_date_edit(due_day)
        self.time_check = QCheckBox("Time")
        self.time_check.setChecked(bool(time_text))
        self.time_edit = make_time_edit(time_text or "09:00")
        self.remind_combo = QComboBox()
        fill_combo(self.remind_combo, REMINDER_OPTIONS, t.get("remind", -1))
        note = QLabel("A reminder without a time rings at 09:00 on the due date.")
        note.setObjectName("mutedText")
        note.setWordWrap(True)

        due_row = QHBoxLayout()
        due_row.addWidget(self.due_check)
        due_row.addWidget(self.date_edit, 1)
        time_row = QHBoxLayout()
        time_row.addWidget(self.time_check)
        time_row.addWidget(self.time_edit, 1)

        form = QFormLayout()
        form.setSpacing(12)
        form.addRow("Task", self.title_edit)
        form.addRow("Priority", self.priority_combo)
        form.addRow("", due_row)
        form.addRow("", time_row)
        form.addRow("Reminder", self.remind_combo)
        form.addRow("", note)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(16)
        layout.addLayout(form)
        layout.addLayout(button_row(self, "Save", task is not None))

        self.due_check.toggled.connect(self.update_states)
        self.time_check.toggled.connect(self.update_states)
        self.update_states()
        self.title_edit.setFocus()

    def update_states(self):
        has_due = self.due_check.isChecked()
        self.date_edit.setEnabled(has_due)
        self.time_check.setEnabled(has_due)
        self.time_edit.setEnabled(has_due and self.time_check.isChecked())
        self.remind_combo.setEnabled(has_due)

    def request_delete(self):
        self.delete_requested = True
        self.accept()

    def save(self):
        title = self.title_edit.text().strip()
        if not title:
            self.title_edit.setFocus()
            return
        has_due = self.due_check.isChecked()
        has_time = has_due and self.time_check.isChecked()
        self.result_task = {
            "id": self.task_id,
            "title": title,
            "done": self.was_done,
            "priority": self.priority_combo.currentData(),
            "due": self.date_edit.date().toPyDate().isoformat() if has_due else "",
            "time": self.time_edit.time().toString("HH:mm") if has_time else "",
            "remind": self.remind_combo.currentData() if has_due else -1,
        }
        self.accept()