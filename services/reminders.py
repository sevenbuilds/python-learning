from datetime import datetime
from PyQt5.QtCore import QObject, QTimer, pyqtSignal

class ReminderService(QObject):
    fired = pyqtSignal(str, str) 
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.timer = QTimer(self)
        self.timer.setInterval(15 * 1000)
        self.timer.timeout.connect(self.check)
        self.timer.start()
        QTimer.singleShot(2000, self.check) 

    def check(self):
        for key, title, body in self.data.due_reminders(datetime.now()):
            self.data.mark_fired(key)          
            self.fired.emit(title, body)