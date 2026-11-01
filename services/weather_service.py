"""Talks to the internet for DayOS: finds the location, then gets the forecast.

Uses free services that need no API key:
  - ipwho.is / ipapi.co   -> approximate location from your IP address
  - Open-Meteo geocoding  -> city name -> coordinates
  - Open-Meteo forecast   -> current weather + 7-day forecast
"""
import json
import urllib.error
import urllib.parse
import urllib.request

from PyQt5.QtCore import QThread, pyqtSignal

HEADERS = {"User-Agent": "DayOS/1.0"}


def get_json(url):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def locate_by_ip():
    """Return (latitude, longitude, place_name) based on the user's IP."""
    try:
        data = get_json("https://ipwho.is/")
        if data.get("success"):
            place = ", ".join(filter(None, [data.get("city"), data.get("country")]))
            return data["latitude"], data["longitude"], place
    except Exception:
        pass  # fall through to the backup service
    data = get_json("https://ipapi.co/json/")
    place = ", ".join(filter(None, [data.get("city"), data.get("country_name")]))
    return data["latitude"], data["longitude"], place


def geocode(name):
    """Return (latitude, longitude, place_name) for a typed city name."""
    query = urllib.parse.urlencode(
        {"name": name, "count": 1, "language": "en", "format": "json"}
    )
    data = get_json(f"https://geocoding-api.open-meteo.com/v1/search?{query}")
    results = data.get("results")
    if not results:
        raise ValueError(f"No place found called '{name}'")
    r = results[0]
    place = ", ".join(filter(None, [r.get("name"), r.get("admin1"), r.get("country")]))
    return r["latitude"], r["longitude"], place


def fetch_forecast(lat, lon):
    query = urllib.parse.urlencode({
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,"
                   "weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,"
                 "precipitation_probability_max",
        "timezone": "auto",
        "forecast_days": 7,
    })
    return get_json(f"https://api.open-meteo.com/v1/forecast?{query}")


class WeatherWorker(QThread):
    """Runs the slow network calls in the background so the UI never freezes."""
    loaded = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, city=None):
        super().__init__()
        self.city = city          # None = detect location from IP

    def run(self):
        try:
            if self.city:
                lat, lon, place = geocode(self.city)
            else:
                lat, lon, place = locate_by_ip()
            data = fetch_forecast(lat, lon)
            data["place"] = place
            self.loaded.emit(data)
        except urllib.error.URLError:
            self.failed.emit("no internet connection")
        except Exception as error:
            self.failed.emit(str(error) or error.__class__.__name__)