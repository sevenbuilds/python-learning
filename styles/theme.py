APP_STYLE = """
QWidget {
    color: #edf0f6;
    font-family: "Segoe UI";
    font-size: 10pt;
}
QMainWindow, #appRoot {
    background-color: #10131b;
}
#sidebar {
    background-color: #191e2a;
    border: 1px solid #2a3040;
    border-radius: 18px;
}
#brand {
    color: #f3f5fb;
    font-size: 17pt;
    font-weight: 700;
    letter-spacing: 2px;
}
#sidebarCaption, #eyebrow, #sectionTitle, #cardCategory, #footerText {
    color: #858fa5;
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 1.5px;
}
#navigationButton {
    text-align: left;
    color: #aeb7c9;
    background: transparent;
    border: none;
    border-radius: 9px;
    padding: 12px 10px;
}
#navigationButton:hover {
    background-color: #252d3d;
    color: #ffffff;
}
#navigationButton[active="true"] {
    background-color: #303c55;
    color: #ffffff;
}
QPushButton#navigationButton[active="true"] {
    background-color: #303744;
    color: white;
}
#pageTitle {
    color: #f4f6fb;
    font-size: 25pt;
    font-weight: 650;
}
#mutedText {
    color: #929db2;
    font-size: 9pt;
}
#clock {
    color: #e7ebf5;
    font-size: 25pt;
    font-weight: 600;
}
#sectionTitle {
    padding-top: 8px;
}
#infoCard {
    background-color: #1a202d;
    border: 1px solid #2b3445;
    border-radius: 16px;
}
#infoCard:hover {
    background-color: #202838;
    border: 1px solid #46536b;
}
#cardCategory {
    color: #8fa8d8;
}
#cardTitle {
    color: #f0f3fa;
    font-size: 15pt;
    font-weight: 600;
}
#cardAction {
    color: #a9c2f2;
    font-size: 9pt;
    font-weight: 600;
}
#modeButton {
    background-color: #1a202d;
    color: #aeb7c9;
    border: 1px solid #2b3445;
    border-radius: 10px;
    padding: 12px 10px;
    font-weight: 600;
}
#modeButton:hover {
    background-color: #202838;
    color: #ffffff;
}
#modeButton:checked {
    background-color: #303c55;
    border: 1px solid #8B9CF6;
    color: #ffffff;
}
#primaryButton {
    background-color: #8B9CF6;
    color: #10131b;
    border: none;
    border-radius: 12px;
    padding: 12px 34px;
    font-weight: 700;
}
#primaryButton:hover {
    background-color: #a3b1f8;
}
#secondaryButton {
    background-color: #252d3d;
    color: #edf0f6;
    border: none;
    border-radius: 12px;
    padding: 12px 28px;
    font-weight: 600;
}
#secondaryButton:hover {
    background-color: #303c55;
}
#smallButton {
    background-color: #252d3d;
    color: #edf0f6;
    border: none;
    border-radius: 10px;
    padding: 10px 14px;
    font-weight: 600;
}
#smallButton:hover {
    background-color: #303c55;
}
#searchInput {
    background-color: #1a202d;
    color: #edf0f6;
    border: 1px solid #2b3445;
    border-radius: 10px;
    padding: 10px 12px;
}
#searchInput:focus {
    border: 1px solid #8B9CF6;
}
#weatherHero {
    background-color: #1a202d;
    border: 1px solid #2b3445;
    border-radius: 18px;
}
#heroIcon {
    font-size: 56pt;
}
#heroTemp {
    color: #f4f6fb;
    font-size: 50pt;
    font-weight: 600;
}
#heroCondition {
    color: #f0f3fa;
    font-size: 15pt;
    font-weight: 600;
}
#statValue {
    color: #f0f3fa;
    font-size: 14pt;
    font-weight: 600;
}
#statLabel {
    color: #858fa5;
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 1.5px;
}
#forecastDay {
    background-color: #1a202d;
    border: 1px solid #2b3445;
    border-radius: 14px;
}
#forecastDay:hover {
    background-color: #202838;
    border: 1px solid #46536b;
}
#forecastDayName {
    color: #8fa8d8;
    font-size: 9pt;
    font-weight: 700;
    letter-spacing: 1px;
}
#forecastIcon {
    font-size: 24pt;
}
#forecastHigh {
    color: #f0f3fa;
    font-size: 13pt;
    font-weight: 600;
}
#forecastLow {
    color: #929db2;
    font-size: 10pt;
}
#forecastRain {
    color: #8fa8d8;
    font-size: 8pt;
}
#notesPanel, #editorPanel {
    background-color: #1a202d;
    border: 1px solid #2b3445;
    border-radius: 16px;
}
#notesList {
    background: transparent;
    border: none;
    outline: none;
}
#notesList::item {
    color: #aeb7c9;
    padding: 12px 10px;
    border-radius: 10px;
    margin-bottom: 2px;
}
#notesList::item:hover {
    background-color: #202838;
    color: #ffffff;
}
#notesList::item:selected {
    background-color: #303c55;
    color: #ffffff;
}
#noteTitle {
    background: transparent;
    border: none;
    color: #f4f6fb;
    font-size: 20pt;
    font-weight: 600;
    padding: 4px 0;
}
#noteBody {
    background: transparent;
    border: none;
    color: #dfe5f2;
    font-size: 11pt;
    selection-background-color: #46536b;
}
#dangerButton {
    background-color: #33232d;
    color: #f2a1a1;
    border: none;
    border-radius: 10px;
    padding: 10px 16px;
    font-weight: 600;
}
#dangerButton:hover {
    background-color: #46293a;
}
#dangerButton:disabled {
    color: #6b5560;
}
QDialog, QMessageBox {
    background-color: #161b26;
}
QLineEdit, QDateEdit, QTimeEdit, QComboBox {
    background-color: #1a202d;
    color: #edf0f6;
    border: 1px solid #2b3445;
    border-radius: 8px;
    padding: 8px 10px;
    selection-background-color: #46536b;
}
QLineEdit:focus, QDateEdit:focus, QTimeEdit:focus, QComboBox:focus {
    border: 1px solid #8B9CF6;
}
QLineEdit:disabled, QDateEdit:disabled, QTimeEdit:disabled, QComboBox:disabled {
    color: #5b6578;
    background-color: #151a25;
}
QComboBox::drop-down, QDateEdit::drop-down {
    border: none;
    width: 26px;
}
QComboBox QAbstractItemView {
    background-color: #1a202d;
    color: #edf0f6;
    border: 1px solid #2b3445;
    selection-background-color: #303c55;
    outline: none;
}
QCheckBox {
    color: #edf0f6;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 5px;
    border: 2px solid #46536b;
    background-color: #1a202d;
}
QCheckBox::indicator:checked {
    background-color: #8B9CF6;
    border-color: #8B9CF6;
}
QCalendarWidget QWidget {
    background-color: #1a202d;
    color: #edf0f6;
}
QCalendarWidget QAbstractItemView {
    background-color: #1a202d;
    color: #edf0f6;
    selection-background-color: #303c55;
    selection-color: #ffffff;
}
QCalendarWidget QToolButton {
    color: #edf0f6;
    background-color: #252d3d;
    border-radius: 6px;
    padding: 4px 8px;
}
 
/* ---------- scrolling ---------- */
QScrollArea {
    background: transparent;
    border: none;
}
#scrollContent {
    background: transparent;
}
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #2f3a4f;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}
 
/* ---------- calendar ---------- */
#calendarPanel, #dayPanel {
    background-color: #1a202d;
    border: 1px solid #2b3445;
    border-radius: 16px;
}
#monthLabel {
    color: #f4f6fb;
    font-size: 17pt;
    font-weight: 600;
}
#weekdayLabel {
    color: #858fa5;
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 1.5px;
}
#dayCell {
    background-color: transparent;
    color: #dfe5f2;
    border: 1px solid transparent;
    border-radius: 12px;
    min-height: 54px;
    font-size: 10pt;
    font-weight: 600;
}
#dayCell:hover {
    background-color: #202838;
}
#dayCell[otherMonth="true"] {
    color: #5b6578;
}
#dayCell[today="true"] {
    color: #8B9CF6;
    border: 1px solid #46536b;
}
#dayCell[selected="true"] {
    background-color: #303c55;
    border: 1px solid #8B9CF6;
    color: #ffffff;
}
#dayTitle {
    color: #f4f6fb;
    font-size: 16pt;
    font-weight: 600;
}
#scheduleRow, #taskRow {
    background-color: #202838;
    border: 1px solid #2b3445;
    border-radius: 12px;
}
#scheduleRow:hover, #taskRow:hover {
    border: 1px solid #46536b;
}
#scheduleTime {
    color: #8fa8d8;
    font-size: 9pt;
    font-weight: 600;
}
#scheduleTitle, #taskTitle {
    color: #f0f3fa;
    font-weight: 600;
}
#scheduleTitle[done="true"], #taskTitle[done="true"] {
    color: #6b7488;
    text-decoration: line-through;
}
#scheduleBadge {
    color: #929db2;
    font-size: 9pt;
}
#iconButton {
    background: transparent;
    color: #858fa5;
    border: none;
    border-radius: 8px;
    padding: 4px 8px;
}
#iconButton:hover {
    background-color: #303c55;
    color: #ffffff;
}
 
/* ---------- tasks ---------- */
#checkButton {
    background: transparent;
    border: 2px solid #46536b;
    border-radius: 13px;
    color: #10131b;
    font-weight: 700;
    min-width: 22px;
    max-width: 22px;
    min-height: 22px;
    max-height: 22px;
    padding: 0;
}
#checkButton:hover {
    border-color: #8B9CF6;
}
#checkButton:checked {
    background-color: #8B9CF6;
    border-color: #8B9CF6;
}
#priorityDot {
    font-size: 9pt;
    color: #6b7488;
}
#priorityDot[level="1"] {
    color: #F2B66D;
}
#priorityDot[level="2"] {
    color: #F28B8B;
}
#dueChip {
    color: #929db2;
    background-color: #252d3d;
    border-radius: 9px;
    padding: 3px 10px;
    font-size: 9pt;
    font-weight: 600;
}
#dueChip[state="today"] {
    color: #8B9CF6;
}
#dueChip[state="overdue"] {
    color: #F28B8B;
}
 
/* ---------- reminder toast ---------- */
#toast {
    background-color: #1a202d;
    border: 1px solid #46536b;
    border-radius: 14px;
}
#toastTitle {
    color: #f4f6fb;
    font-size: 11pt;
    font-weight: 700;
}
"""
