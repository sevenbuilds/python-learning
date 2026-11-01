import os
import json
import uuid
from datetime import datetime, date, time, timedelta
from PyQt5.QtCore import QObject, pyqtSignal

HOME = os.path.expanduser("~")
DATA_FOLDER = os.path.join(HOME, ".dayos")
DATA_FILE = os.path.join(DATA_FOLDER, "planner.json")

#--- colors ---
COLORS = [
    ("Indigo", "#8B9CF6"),
    ("Green", "#6FCF97"),
    ("Amber", "#F2B66D"),
    ("Rose", "#F28BA8"),
    ("Sky", "#6EC6F5")
]

#---- reminder options ---
REMINDER_OPTIONS = [
    ("No reminder", -1),
    ("At the time", 0),
    ("5 minutes before", 5),
    ("10 minutes before", 10),
    ("30 minutes before", 30),
    ("1 hour before", 60),
    ("1 day before", 1440)
]
REPEAT_OPTIONS = [
    ("Does not repeat", "none"),
    ("Every day", "daily"),
    ("Every week", "weekly"),
    ("Every month", "monthly")
]
PRIORITIES = [
    ("Low", 0),
    ("Medium", 1),
    ("High", 2)
]

def new_id():
    return uuid.uuid4().hex

def parse_time(text):
    return datetime.strptime(text, "%H:%M").time()

def describe_when(start, now):
    delta = int((start - now).total_seconds() // 60)
    if start.date() == now.date():
        if delta < -1:
            return f"Started {-delta} min ago · {start:%H:%M}"
        if delta < 1:
            return f"Starting now · {start:%H:%M}"
        if delta < 60:
            return f"In {delta} min · {start:%H:%M}"
        return f"Today at {start:%H:%M}"
    if start.date() == now.date() + timedelta(days=1):
        return f"Tomorrow at {start:%H:%M}"
    return f"{start:%a %d %b} at {start:%H:%M}"

class PlannerData(QObject):
    changed = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.events = []
        self.tasks = []
        self.fired = {}

        self.load()

    # ---- loading and saving ---
    def load(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                notes_data = json.load(file)
            self.events = notes_data.get("events", [])
            self.tasks = notes_data.get("tasks", [])
            self.fired = notes_data.get("fired", {})
        except FileNotFoundError:
            pass
        except (json.JSONDecodeError, AttributeError):
            backup = DATA_FILE + ".corrupt"
            os.replace(DATA_FILE, backup)

    def save(self):
        os.makedirs(DATA_FOLDER, exist_ok=True)
        temp_file = DATA_FILE + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "events": self.events,
                    "tasks": self.tasks,
                    "fired": self.fired
                },
                file,
                ensure_ascii=False,
                indent=2
            )
        os.replace(temp_file, DATA_FILE)

    def commit(self):
        self.save()
        self.changed.emit()

    def find_event(self, event_id):
        for event in self.events:
            if event["id"] == event_id:
                return event
        return None

    def upsert_event(self, event):
        for i, existing in enumerate(self.events):
            if existing["id"] == event["id"]:
                self.events[i] = event
                break
        else:
            self.events.append(event)
        self.commit()

    def delete_event(self, event_id):
        self.events = [
            event for event in self.events
            if event["id"] != event_id
        ]
        self.commit()

    def find_task(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    def upsert_task(self, task):
        for i, existing in enumerate(self.tasks):
            if existing["id"] == task["id"]:
                self.tasks[i] = task
                break
        else:
            self.tasks.append(task)
        self.commit()

    def delete_task(self, task_id):
        self.tasks = [
            task for task in self.tasks
            if task["id"] != task_id
        ]
        self.commit()

    def toggle_task(self, task_id):
        task = self.find_task(task_id)
        if task:
            task["done"] = not task.get("done", False)
            self.commit()

    def clear_done(self):
        self.tasks = [
            task for task in self.tasks
            if not task.get("done")
        ]
        self.commit()

    @staticmethod
    def occurs_on(event, day):
        first = date.fromisoformat(event["date"])
        if day < first:
            return False
        repeat = event.get("repeat", "none")
        if repeat == "daily":
            return True
        if repeat == "weekly":
            return (day - first).days % 7 == 0
        if repeat == "monthly":
            return day.day == first.day
        return day == first
    
    def items_on(self, day):
        items = []
        for event in self.events:
            if self.occurs_on(event, day):
                items.append({
                    "kind": "event",
                    "id": event["id"],
                    "title": event["title"],
                    "start": event.get("start", ""),
                    "end": event.get("end", ""),
                    "color": event.get("color", "#8B9CF6"),
                    "remind": event.get("remind", -1),
                    "repeat": event.get("repeat", "none")
                })
        day_string = day.isoformat()
        for task in self.tasks:
            if task.get("due") == day_string:
                items.append({
                    "kind": "task",
                    "id": task["id"],
                    "title": task["title"],
                    "start": task.get("time", ""),
                    "end": "",
                    "done": task.get("done", False),
                    "priority": task.get("priority", 1),
                    "remind": task.get("remind", -1),
                    "repeat": "none"
                })
        items.sort(
            key=lambda item: (
                item["start"] == "",
                item["start"],
                item["kind"]
            )
        )
        return items

    def count_on(self, day):
        return len(self.items_on(day))
    
    def mark_fired(self, key):
            now = datetime.now()
            self.fired[key] = now.isoformat(timespec="seconds")
    
            #---- remove old reminder keys ----
            cutoff = now - timedelta(days=3)
            self.fired = {
                k: v for k, v in self.fired.items()
                if datetime.fromisoformat(v) > cutoff
            }
            self.save()

    def tasks_summary(self, today):
            if not self.tasks:
                return "No tasks yet", "Capture what you need to get done."
            open_tasks = [
                task for task in self.tasks
                if not task.get("done")
            ]
            if not open_tasks:
                return "All done 🎉", "Every task is checked off."
    
            today_string = today.isoformat()
    
            due_today = sum(
                1 for task in open_tasks
                if task.get("due") == today_string
            )
            overdue = sum(
                1 for task in open_tasks
                if task.get("due") and task["due"] < today_string
            )
            parts = [f"{due_today} due today"]
            if overdue:
                parts.append(f"{overdue} overdue")
    
            count = len(open_tasks)
            return (
                f"{count} open task{'s' if count != 1 else ''}",
                " · ".join(parts)
            )

    def next_up(self, now):
        best = None
        for offset in range(31):
            day = now.date() + timedelta(days=offset)
            for event in self.events:
                if self.occurs_on(event, day):
                    start = datetime.combine(
                        day,
                        parse_time(event["start"])
                    )
                    if start >= now and (best is None or start < best[0]):
                        best = (start, event["title"])
            for task in self.tasks:
                if task.get("done") or task.get("due") != day.isoformat() or not task.get("time"):
                    continue
                start = datetime.combine(
                    day,
                    parse_time(task["time"])
                )
                if start >= now and (best is None or start < best[0]):
                    best = (start, "☑ " + task["title"])
            if best:
                break
        if best is None:
            return (
                "Nothing scheduled",
                "Calendar events and reminders will appear here."
            )
        return best[1], describe_when(best[0], now)

    def due_reminders(self, now):
            found = []
            for event in self.events:
                minutes = event.get("remind", -1)
                if minutes < 0:
                    continue
                for offset in range(-1, 3):
                    day = now.date() + timedelta(days=offset)
                    if not self.occurs_on(event, day):
                        continue
                    start = datetime.combine(
                        day,
                        parse_time(event["start"])
                    )
                    trigger = start - timedelta(minutes=minutes)
                    key = f"e:{event['id']}:{day.isoformat()}"
                    if trigger <= now <= start + timedelta(minutes=30) and key not in self.fired:
                        found.append((
                            key,
                            "🔔 " + event["title"],
                            describe_when(start, now)
                        ))
                        
            for task in self.tasks:
                minutes = task.get("remind", -1)
                if task.get("done") or minutes < 0 or not task.get("due"):
                    continue
                if task.get("time"):
                    task_time = parse_time(task["time"])
                else:
                    task_time = time(9, 0)
                due_date = datetime.combine(
                    date.fromisoformat(task["due"]),
                    task_time
                )
                trigger = due_date - timedelta(minutes=minutes)
                key = f"t:{task['id']}:{task['due']}:{task_time:%H:%M}"
                if trigger <= now <= due_date + timedelta(minutes=30) and key not in self.fired:
                    found.append((
                        key,
                        "☑ " + task["title"],
                        "Task due · " + describe_when(due_date, now)
                    ))
            return found

