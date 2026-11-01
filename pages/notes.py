import uuid
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QMessageBox,
    QShortcut,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QKeySequence
from services.notes_store import load_notes, save_notes


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


class notespage(QWidget):
    # sends (title, description) so the Home "Quick notes" card stays up to date
    summary_changed = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setObjectName("notesPage")

        self.notes = load_notes()       # list of dicts: id, title, body, created, updated
        self.current_id = None          # note open in the editor
        self.loading = False            # True while we fill the editor from code
        self.dirty = False              # unsaved changes?

        # wait 600 ms after the last keystroke, then save
        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.setInterval(600)
        self.save_timer.timeout.connect(self.autosave)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(20)

        # ---- header ----
        header = QVBoxLayout()
        eyebrow = QLabel("YOUR IDEAS")
        eyebrow.setObjectName("eyebrow")
        title = QLabel("Notes")
        title.setObjectName("pageTitle")
        self.count_label = QLabel("")
        self.count_label.setObjectName("mutedText")
        header.addWidget(eyebrow)
        header.addWidget(title)
        header.addWidget(self.count_label)
        main_layout.addLayout(header)

        body = QHBoxLayout()
        body.setSpacing(16)

        # ---- left panel: search + new + list ----
        left = QFrame()
        left.setObjectName("notesPanel")
        left.setFixedWidth(300)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(14, 14, 14, 14)
        left_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("Search notes…")
        self.search_input.textChanged.connect(self.refresh_list)

        self.new_button = QPushButton("+  New note")
        self.new_button.setObjectName("primaryButton")
        self.new_button.setCursor(Qt.PointingHandCursor)
        self.new_button.clicked.connect(self.new_note)

        self.list = QListWidget()
        self.list.setObjectName("notesList")
        self.list.setCursor(Qt.PointingHandCursor)
        self.list.currentItemChanged.connect(self.on_selection_changed)

        left_layout.addWidget(self.search_input)
        left_layout.addWidget(self.new_button)
        left_layout.addWidget(self.list, 1)

        # ---- right panel: editor ----
        right = QFrame()
        right.setObjectName("editorPanel")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(24, 20, 24, 16)
        right_layout.setSpacing(8)

        self.title_edit = QLineEdit()
        self.title_edit.setObjectName("noteTitle")
        self.title_edit.setPlaceholderText("Title")
        self.title_edit.textChanged.connect(self.on_edited)

        self.meta_label = QLabel("")
        self.meta_label.setObjectName("mutedText")

        self.body_edit = QTextEdit()
        self.body_edit.setObjectName("noteBody")
        self.body_edit.setAcceptRichText(False)       # paste as plain text
        self.body_edit.setPlaceholderText("Start writing…")
        self.body_edit.textChanged.connect(self.on_edited)

        footer = QHBoxLayout()
        self.words_label = QLabel("")
        self.words_label.setObjectName("mutedText")
        self.delete_button = QPushButton("Delete")
        self.delete_button.setObjectName("dangerButton")
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.clicked.connect(self.delete_note)
        footer.addWidget(self.words_label)
        footer.addStretch()
        footer.addWidget(self.delete_button)

        right_layout.addWidget(self.title_edit)
        right_layout.addWidget(self.meta_label)
        right_layout.addWidget(self.body_edit, 1)
        right_layout.addLayout(footer)

        body.addWidget(left)
        body.addWidget(right, 1)
        main_layout.addLayout(body, 1)

        # Ctrl+N works anywhere on this page
        shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        shortcut.activated.connect(self.new_note)

        # ---- first load ----
        self.refresh_list()
        if self.list.count():
            self.list.setCurrentItem(self.list.item(0))   # triggers on_selection_changed
        else:
            self.clear_editor()

    # ------------------------------------------------------------------
    # helpers
    def find(self, note_id):
        for note in self.notes:
            if note["id"] == note_id:
                return note
        return None

    def item_text(self, note):
        title = note["title"].strip() or "Untitled note"
        preview = " ".join(note["body"].split())[:60] or "No content"
        return f"{title}\n{preview}"

    def meta_text(self, note):
        when = datetime.fromisoformat(note["updated"]).strftime("%d %b, %H:%M")
        return f"Edited {when}"

    def has_content(self, note):
        return bool(note["title"].strip() or note["body"].strip())

    # ------------------------------------------------------------------
    # list on the left
    def refresh_list(self):
        query = self.search_input.text().strip().lower()
        ordered = sorted(self.notes, key=lambda n: n["updated"], reverse=True)

        self.list.blockSignals(True)          # don't fire "selection changed" while rebuilding
        self.list.clear()
        shown = 0
        for note in ordered:
            if query and query not in note["title"].lower() and query not in note["body"].lower():
                continue
            item = QListWidgetItem(self.item_text(note))
            item.setData(Qt.UserRole, note["id"])
            self.list.addItem(item)
            shown += 1
            if note["id"] == self.current_id:
                self.list.setCurrentItem(item)
        self.list.blockSignals(False)

        saved = [n for n in self.notes if self.has_content(n)]
        total = len(saved)
        if query:
            self.count_label.setText(f"{shown} of {total} notes match")
        else:
            self.count_label.setText(
                "Nothing here yet. Press + New note." if total == 0
                else f"{total} note{'s' if total != 1 else ''}"
            )

    def on_selection_changed(self, current, previous):
        if current is None:
            return
        note_id = current.data(Qt.UserRole)
        if note_id == self.current_id:
            return
        self.flush()
        self.open_note(note_id)

    # ------------------------------------------------------------------
    # editor on the right
    def open_note(self, note_id):
        note = self.find(note_id)
        if note is None:
            return
        self.current_id = note_id
        self.loading = True                   # so on_edited ignores these changes
        self.title_edit.setText(note["title"])
        self.body_edit.setPlainText(note["body"])
        self.loading = False
        self.meta_label.setText(self.meta_text(note))
        self.words_label.setText(f"{len(note['body'].split())} words")
        for widget in (self.title_edit, self.body_edit, self.delete_button):
            widget.setEnabled(True)

    def clear_editor(self):
        self.current_id = None
        self.loading = True
        self.title_edit.clear()
        self.body_edit.clear()
        self.loading = False
        self.meta_label.setText("")
        self.words_label.setText("")
        for widget in (self.title_edit, self.body_edit, self.delete_button):
            widget.setEnabled(False)

    def on_edited(self):
        if self.loading or self.current_id is None:
            return
        note = self.find(self.current_id)
        note["title"] = self.title_edit.text()
        note["body"] = self.body_edit.toPlainText()
        note["updated"] = now_iso()
        self.dirty = True
        self.meta_label.setText(self.meta_text(note))
        self.words_label.setText(f"{len(note['body'].split())} words")
        item = self.list.currentItem()
        if item is not None and item.data(Qt.UserRole) == note["id"]:
            item.setText(self.item_text(note))
        self.save_timer.start()               # restarts the 600 ms countdown

    # ------------------------------------------------------------------
    # actions
    def new_note(self):
        self.flush()
        current = self.find(self.current_id) if self.current_id else None
        if current and not self.has_content(current):
            self.title_edit.setFocus()        # already on a blank note, reuse it
            return
        stamp = now_iso()
        note = {"id": uuid.uuid4().hex, "title": "", "body": "",
                "created": stamp, "updated": stamp}
        self.notes.append(note)
        self.search_input.blockSignals(True)
        self.search_input.clear()
        self.search_input.blockSignals(False)
        self.current_id = note["id"]
        self.refresh_list()
        self.open_note(note["id"])
        self.title_edit.setFocus()

    def delete_note(self):
        note = self.find(self.current_id)
        if note is None:
            return
        if self.has_content(note):
            name = note["title"].strip() or "this note"
            answer = QMessageBox.question(
                self, "Delete note", f"Delete “{name}”? This can't be undone."
            )
            if answer != QMessageBox.Yes:
                return
        self.notes = [n for n in self.notes if n["id"] != note["id"]]
        self.current_id = None
        self.save_timer.stop()
        self.dirty = True
        self.save_now()
        self.refresh_list()
        if self.list.count():
            self.list.setCurrentItem(self.list.item(0))
        else:
            self.clear_editor()

    # ------------------------------------------------------------------
    # saving
    def save_now(self):
        saved = [n for n in self.notes if self.has_content(n)]   # skip empty drafts
        save_notes(saved)
        self.dirty = False
        self.emit_summary()

    def autosave(self):
        self.save_now()
        self.refresh_list()                   # re-sort so the edited note jumps to the top

    def flush(self):
        """Save right away if there are unsaved changes (used when switching or closing)."""
        self.save_timer.stop()
        if self.dirty:
            self.save_now()

    def emit_summary(self):
        saved = [n for n in self.notes if self.has_content(n)]
        if not saved:
            self.summary_changed.emit(
                "Nothing to capture yet", "Note down an idea before it disappears."
            )
            return
        latest = max(saved, key=lambda n: n["updated"])
        name = latest["title"].strip() or " ".join(latest["body"].split())[:40] or "Untitled note"
        count = len(saved)
        self.summary_changed.emit(
            f"{count} note{'s' if count != 1 else ''}",
            f"Latest: {name}",
        )