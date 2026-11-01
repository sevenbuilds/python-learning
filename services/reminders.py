from datetime import datetime

from PyQt5.QtCore import QObject, QTimer, pyqtSignal


class ReminderService(QObject):
    """Checks every 15 seconds whether any reminder is due, then emits `fired`."""
    fired = pyqtSignal(str, str)           # title, body

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.timer = QTimer(self)
        self.timer.setInterval(15 * 1000)
        self.timer.timeout.connect(self.check)
        self.timer.start()
        QTimer.singleShot(2000, self.check)    # also check shortly after startup

    def check(self):
        for key, title, body in self.data.due_reminders(datetime.now()):
            self.data.mark_fired(key)          # remember it so it only rings once
            self.fired.emit(title, body)