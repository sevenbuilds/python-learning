from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QFrame,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from services.weather_service import WeatherWorker

# Open-Meteo returns a numeric "weather code"; this turns it into text + emoji.
_GROUPS = [
    ([0], "Clear sky", "☀️"),
    ([1], "Mainly clear", "🌤️"),
    ([2], "Partly cloudy", "⛅"),
    ([3], "Overcast", "☁️"),
    ([45, 48], "Foggy", "🌫️"),
    ([51, 53, 55], "Drizzle", "🌦️"),
    ([56, 57], "Freezing drizzle", "🌧️"),
    ([61, 63, 65], "Rain", "🌧️"),
    ([66, 67], "Freezing rain", "🌧️"),
    ([71, 73, 75, 77], "Snow", "❄️"),
    ([80, 81, 82], "Rain showers", "🌦️"),
    ([85, 86], "Snow showers", "🌨️"),
    ([95], "Thunderstorm", "⛈️"),
    ([96, 99], "Thunderstorm with hail", "⛈️"),
]
WEATHER_CODES = {code: (text, icon) for codes, text, icon in _GROUPS for code in codes}


def describe(code):
    return WEATHER_CODES.get(code, ("Unknown", "🌡️"))


class DayCard(QFrame):
    """One small card in the 7-day row."""
    def __init__(self):
        super().__init__()
        self.setObjectName("forecastDay")
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(10, 14, 10, 14)
        vbox.setSpacing(6)
        self.day = QLabel("--")
        self.day.setObjectName("forecastDayName")
        self.icon = QLabel("--")
        self.icon.setObjectName("forecastIcon")
        self.high = QLabel("--")
        self.high.setObjectName("forecastHigh")
        self.low = QLabel("--")
        self.low.setObjectName("forecastLow")
        self.rain = QLabel("--")
        self.rain.setObjectName("forecastRain")
        for label in (self.day, self.icon, self.high, self.low, self.rain):
            label.setAlignment(Qt.AlignCenter)
            vbox.addWidget(label)

    def set_data(self, day, icon, high, low, rain):
        self.day.setText(day)
        self.icon.setText(icon)
        self.high.setText(high)
        self.low.setText(low)
        self.rain.setText(f"💧 {rain}%")


class weatherpage(QWidget):
    # sends (title, description) so the Home card can show live weather too
    summary_changed = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setObjectName("weatherPage")

        self.data = None              # last forecast we received
        self.city = None              # None = detect by IP, otherwise a typed city
        self.use_fahrenheit = False
        self.worker = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(20)

        # ---- top row: heading (left) + controls (right) ----
        top = QHBoxLayout()
        heading = QVBoxLayout()
        eyebrow = QLabel("YOUR SURROUNDINGS")
        eyebrow.setObjectName("eyebrow")
        title = QLabel("Weather")
        title.setObjectName("pageTitle")
        self.location_label = QLabel("Finding your location…")
        self.location_label.setObjectName("mutedText")
        heading.addWidget(eyebrow)
        heading.addWidget(title)
        heading.addWidget(self.location_label)

        controls = QHBoxLayout()
        controls.setSpacing(8)
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("Search a city…")
        self.search_input.setFixedWidth(190)
        self.search_input.returnPressed.connect(self.search_city)

        self.here_button = QPushButton("📍 My location")
        self.unit_button = QPushButton("°C")
        self.refresh_button = QPushButton("↻ Refresh")
        for button in (self.here_button, self.unit_button, self.refresh_button):
            button.setObjectName("smallButton")
            button.setCursor(Qt.PointingHandCursor)
        self.here_button.clicked.connect(self.use_my_location)
        self.unit_button.clicked.connect(self.toggle_units)
        self.refresh_button.clicked.connect(lambda: self.refresh())

        controls.addWidget(self.search_input)
        controls.addWidget(self.here_button)
        controls.addWidget(self.unit_button)
        controls.addWidget(self.refresh_button)

        top.addLayout(heading)
        top.addStretch()
        top.addLayout(controls)
        top.setAlignment(controls, Qt.AlignTop)
        main_layout.addLayout(top)

        # ---- status line (loading / errors / last updated) ----
        self.status = QLabel("")
        self.status.setObjectName("mutedText")
        main_layout.addWidget(self.status)

        # ---- hero card: current conditions ----
        hero = QFrame()
        hero.setObjectName("weatherHero")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(28, 22, 28, 22)
        hero_layout.setSpacing(24)

        self.hero_icon = QLabel("⏳")
        self.hero_icon.setObjectName("heroIcon")

        left = QVBoxLayout()
        left.setSpacing(2)
        self.hero_temp = QLabel("--°")
        self.hero_temp.setObjectName("heroTemp")
        self.hero_condition = QLabel("Loading…")
        self.hero_condition.setObjectName("heroCondition")
        self.hero_feels = QLabel("")
        self.hero_feels.setObjectName("mutedText")
        left.addWidget(self.hero_temp)
        left.addWidget(self.hero_condition)
        left.addWidget(self.hero_feels)

        stats = QHBoxLayout()
        stats.setSpacing(34)
        box, self.stat_humidity = self.make_stat("HUMIDITY")
        stats.addLayout(box)
        box, self.stat_wind = self.make_stat("WIND")
        stats.addLayout(box)
        box, self.stat_range = self.make_stat("HIGH / LOW")
        stats.addLayout(box)
        box, self.stat_rain = self.make_stat("RAIN CHANCE")
        stats.addLayout(box)

        hero_layout.addWidget(self.hero_icon)
        hero_layout.addLayout(left)
        hero_layout.addStretch()
        hero_layout.addLayout(stats)
        main_layout.addWidget(hero)

        # ---- 7-day forecast ----
        section = QLabel("7-DAY FORECAST")
        section.setObjectName("sectionTitle")
        main_layout.addWidget(section)

        days_row = QHBoxLayout()
        days_row.setSpacing(12)
        self.day_cards = []
        for _ in range(7):
            card = DayCard()
            days_row.addWidget(card, 1)
            self.day_cards.append(card)
        main_layout.addLayout(days_row)

        main_layout.addStretch()

        # ---- refresh automatically every 30 minutes ----
        self.auto_timer = QTimer(self)
        self.auto_timer.setInterval(30 * 60 * 1000)
        self.auto_timer.timeout.connect(lambda: self.refresh())
        self.auto_timer.start()

        self.refresh()

    # ------------------------------------------------------------------
    def make_stat(self, caption):
        box = QVBoxLayout()
        box.setSpacing(2)
        value = QLabel("--")
        value.setObjectName("statValue")
        label = QLabel(caption)
        label.setObjectName("statLabel")
        box.addWidget(value)
        box.addWidget(label)
        return box, value

    def temp(self, celsius):
        """Format a Celsius number in the unit the user picked."""
        if self.use_fahrenheit:
            return f"{round(celsius * 9 / 5 + 32)}°"
        return f"{round(celsius)}°"

    # ---- actions ----
    def refresh(self, city="__keep__"):
        if city != "__keep__":
            self.city = city
        if self.worker is not None and self.worker.isRunning():
            self.status.setText("Still loading, give it a moment…")
            return
        self.status.setText("Fetching weather…")
        self.worker = WeatherWorker(self.city)
        self.worker.loaded.connect(self.on_loaded)
        self.worker.failed.connect(self.on_failed)
        self.worker.start()

    def search_city(self):
        text = self.search_input.text().strip()
        if text:
            self.refresh(text)

    def use_my_location(self):
        self.search_input.clear()
        self.refresh(None)

    def toggle_units(self):
        self.use_fahrenheit = not self.use_fahrenheit
        self.unit_button.setText("°F" if self.use_fahrenheit else "°C")
        if self.data:
            self.render()          # no need to re-download, just redraw

    # ---- worker results ----
    def on_loaded(self, data):
        self.data = data
        self.render()
        self.status.setText(f"Updated {datetime.now():%H:%M}")

    def on_failed(self, message):
        self.status.setText(f"Couldn't load weather: {message}")
        if self.data is None:
            self.location_label.setText("Location unavailable")
            self.summary_changed.emit("Weather unavailable", "Check your internet connection.")

    # ---- drawing the data ----
    def render(self):
        d = self.data
        current = d["current"]
        daily = d["daily"]

        text, icon = describe(current["weather_code"])
        self.location_label.setText(d["place"])
        self.hero_icon.setText(icon)
        self.hero_temp.setText(self.temp(current["temperature_2m"]))
        self.hero_condition.setText(text)
        self.hero_feels.setText(f"Feels like {self.temp(current['apparent_temperature'])}")

        high = self.temp(daily["temperature_2m_max"][0])
        low = self.temp(daily["temperature_2m_min"][0])
        rain_today = daily["precipitation_probability_max"][0] or 0

        self.stat_humidity.setText(f"{current['relative_humidity_2m']}%")
        self.stat_wind.setText(f"{round(current['wind_speed_10m'])} km/h")
        self.stat_range.setText(f"{high} / {low}")
        self.stat_rain.setText(f"{rain_today}%")

        for i, card in enumerate(self.day_cards):
            if i >= len(daily["time"]):
                card.hide()
                continue
            card.show()
            date = datetime.strptime(daily["time"][i], "%Y-%m-%d")
            name = "Today" if i == 0 else date.strftime("%a")
            _, day_icon = describe(daily["weather_code"][i])
            card.set_data(
                name,
                day_icon,
                self.temp(daily["temperature_2m_max"][i]),
                self.temp(daily["temperature_2m_min"][i]),
                daily["precipitation_probability_max"][i] or 0,
            )

        self.summary_changed.emit(
            f"{icon} {text}",
            f"{d['place']} · {self.temp(current['temperature_2m'])} now, "
            f"feels like {self.temp(current['apparent_temperature'])}. "
            f"Today: high {high}, low {low}.",
        )