from datetime import date, timedelta

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFrame, QButtonGroup, QDialog,
)
from PyQt5.QtCore import Qt, pyqtSignal
from services.planner_data import new_id
from widgets.helpers import clear_layout, make_scroll
from widgets.planner_dialogs import TaskDialog


def due_text(task, today):
    """Returns (label, state) for the little due-date chip."""
    due = task.get("due")
    if not due:
        return "", ""
    d = date.fromisoformat(due)
    if d < today and not task.get("done"):
        label, state = f"Overdue · {d:%d %b}", "overdue"
    elif d == today:
        label, state = "Today", "today"
    elif d == today + timedelta(days=1):
        label, state = "Tomorrow", "normal"
    else:
        label, state = f"{d:%a %d %b}", "normal"
    if task.get("time"):
        label += f" · {task['time']}"
    return label, state


class TaskRow(QFrame):
    toggled = pyqtSignal(str)
    edit_requested = pyqtSignal(str)
    delete_requested = pyqtSignal(str)

    def __init__(self, task, today):
        super().__init__()
        self.setObjectName("taskRow")
        done = task.get("done", False)
        task_id = task["id"]
        row = QHBoxLayout(self)
        row.setContentsMargins(14, 10, 10, 10)
        row.setSpacing(12)

        check = QPushButton("✓" if done else "")
        check.setObjectName("checkButton")
        check.setCheckable(True)
        check.setChecked(done)
        check.setCursor(Qt.PointingHandCursor)
        check.clicked.connect(lambda: self.toggled.emit(task_id))

        dot = QLabel("●")
        dot.setObjectName("priorityDot")
        dot.setProperty("level", str(task.get("priority", 1)))
        dot.setToolTip(["Low priority", "Medium priority", "High priority"][task.get("priority", 1)])

        title = QLabel(task["title"])
        title.setObjectName("taskTitle")
        title.setWordWrap(True)
        title.setProperty("done", done)

        row.addWidget(check)
        row.addWidget(dot)
        row.addWidget(title, 1)

        label, state = due_text(task, today)
        if label:
            chip = QLabel(label)
            chip.setObjectName("dueChip")
            chip.setProperty("state", state)
            row.addWidget(chip)
        if task.get("remind", -1) >= 0 and task.get("due") and not done:
            bell = QLabel("🔔")
            bell.setObjectName("scheduleBadge")
            row.addWidget(bell)

        edit = QPushButton("✎")
        edit.setObjectName("iconButton")
        edit.setCursor(Qt.PointingHandCursor)
        edit.clicked.connect(lambda: self.edit_requested.emit(task_id))
        remove = QPushButton("✕")
        remove.setObjectName("iconButton")
        remove.setCursor(Qt.PointingHandCursor)
        remove.clicked.connect(lambda: self.delete_requested.emit(task_id))
        row.addWidget(edit)
        row.addWidget(remove)


class taskspage(QWidget):
    FILTERS = [("all", "All"), ("today", "Today"), ("upcoming", "Upcoming"), ("done", "Done")]

    def __init__(self, data):
        super().__init__()
        self.setObjectName("tasksPage")
        self.data = data
        self.filter = "all"

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(16)

        header = QVBoxLayout()
        eyebrow = QLabel("STAY ON TRACK")
        eyebrow.setObjectName("eyebrow")
        title = QLabel("Tasks")
        title.setObjectName("pageTitle")
        self.subtitle = QLabel("")
        self.subtitle.setObjectName("mutedText")
        header.addWidget(eyebrow)
        header.addWidget(title)
        header.addWidget(self.subtitle)
        main_layout.addLayout(header)

        # ---- quick add ----
        add_row = QHBoxLayout()
        add_row.setSpacing(10)
        self.input = QLineEdit()
        self.input.setObjectName("searchInput")
        self.input.setPlaceholderText("Add a task and press Enter…")
        self.input.returnPressed.connect(self.add_quick)
        more = QPushButton("Due date, priority, reminder…")
        more.setObjectName("smallButton")
        more.setCursor(Qt.PointingHandCursor)
        more.clicked.connect(self.add_detailed)
        add_row.addWidget(self.input, 1)
        add_row.addWidget(more)
        main_layout.addLayout(add_row)

        # ---- filter tabs ----
        tabs = QHBoxLayout()
        tabs.setSpacing(10)
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        for key, label in self.FILTERS:
            button = QPushButton(label)
            button.setObjectName("modeButton")
            button.setCheckable(True)
            button.setChecked(key == "all")
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(lambda _c, k=key: self.set_filter(k))
            self.group.addButton(button)
            tabs.addWidget(button)
        tabs.addStretch()
        clear = QPushButton("Clear completed")
        clear.setObjectName("smallButton")
        clear.setCursor(Qt.PointingHandCursor)
        clear.clicked.connect(self.data.clear_done)
        tabs.addWidget(clear)
        main_layout.addLayout(tabs)

        # ---- list ----
        scroll, self.rows_layout = make_scroll()
        main_layout.addWidget(scroll, 1)

        self.data.changed.connect(self.refresh)
        self.refresh()

    # ------------------------------------------------------------------
    def set_filter(self, key):
        self.filter = key
        self.refresh()

    def visible(self, task, today_iso):
        done = task.get("done", False)
        due = task.get("due", "")
        if self.filter == "done":
            return done
        if self.filter == "today":
            return (not done) and due != "" and due <= today_iso     # includes overdue
        if self.filter == "upcoming":
            return (not done) and due > today_iso
        return True

    def refresh(self):
        today = date.today()
        today_iso = today.isoformat()
        tasks = [t for t in self.data.tasks if self.visible(t, today_iso)]
        tasks.sort(key=lambda t: (t.get("done", False), t.get("due") or "9999-99-99",
                                  t.get("time") or "99:99", -t.get("priority", 1)))

        open_count = sum(1 for t in self.data.tasks if not t.get("done"))
        done_count = len(self.data.tasks) - open_count
        self.subtitle.setText(f"{open_count} open · {done_count} done")

        clear_layout(self.rows_layout)
        if not tasks:
            empty = QLabel("Nothing here. Enjoy the calm ✨")
            empty.setObjectName("mutedText")
            self.rows_layout.addWidget(empty)
        for task in tasks:
            row = TaskRow(task, today)
            row.toggled.connect(self.data.toggle_task)
            row.edit_requested.connect(self.edit_task)
            row.delete_requested.connect(self.data.delete_task)
            self.rows_layout.addWidget(row)
        self.rows_layout.addStretch()

    # ---- actions ----
    def add_quick(self):
        text = self.input.text().strip()
        if not text:
            return
        self.data.upsert_task({"id": new_id(), "title": text, "done": False,
                               "priority": 1, "due": "", "time": "", "remind": -1})
        self.input.clear()

    def add_detailed(self):
        dialog = TaskDialog(self, title=self.input.text().strip())
        if dialog.exec_() == QDialog.Accepted and dialog.result_task:
            self.data.upsert_task(dialog.result_task)
            self.input.clear()

    def edit_task(self, task_id):
        task = self.data.find_task(task_id)
        if task is None:
            return
        dialog = TaskDialog(self, task=task)
        if dialog.exec_() == QDialog.Accepted:
            if dialog.delete_requested:
                self.data.delete_task(task_id)
            elif dialog.result_task:
                self.data.upsert_task(dialog.result_task)