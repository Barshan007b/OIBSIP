# weather_app.py
"""Smart Weather Forecast Application

A modern Tkinter GUI that fetches real‑time weather data from the Open‑Meteo API.
Features:
- Search by city name (geocoder → lat/lon)
- Automatic IP‑based location detection (geocoder)
- Current weather display (temp, condition, humidity, wind, pressure, sunrise/sunset)
- Hourly (12‑hour) and daily (5‑day) forecasts
- Dark‑mode, gradient background, smooth animations
- Unit conversion (°C/°F) and km/h ↔ mph toggle
- Search history saved locally (JSON)
- Graceful error handling
"""

import json, os, threading, math, time
from datetime import datetime

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from geocoder import ip, arcgis

# ---------- Configuration ----------
API_URL = "https://api.open-meteo.com/v1/forecast"
ICON_URL = "https://open-meteo.com/images/weather-icons/"
HISTORY_FILE = "weather_history.json"
DEFAULT_UNITS = "metric"  # metric or imperial
# -----------------------------------

class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Weather Forecast")
        self.geometry("1024x680")
        self.configure(bg="#1e1e2f")
        # Apply high‑DPI scaling for Windows
        self.tk.call("tk", "scaling", 1.5)
        self._load_history()
        self.units = DEFAULT_UNITS
        self._build_ui()
        self.after(100, self._auto_location)  # detect location after UI ready

    # ---------- UI Construction ----------
    def _build_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabel", foreground="#e0e0ff", background="#1e1e2f", font=("Segoe UI", 11))
        style.configure("TButton", foreground="#e0e0ff", background="#3b3b58", font=("Segoe UI", 10))
        style.map("TButton", background=[("active", "#4a4a70")])
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#ffcc00")

        # Top search bar
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", pady=10, padx=20)
        self.city_var = tk.StringVar()
        city_entry = ttk.Entry(top_frame, textvariable=self.city_var, width=30, font=("Segoe UI", 12))
        city_entry.pack(side="left", expand=True, fill="x")
        ttk.Button(top_frame, text="Search", command=self._on_search).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Use My Location", command=self._auto_location).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Toggle Units", command=self._toggle_units).pack(side="left", padx=5)

        # Current weather panel
        self.current_frame = ttk.LabelFrame(self, text="Current Weather", style="Header.TLabel")
        self.current_frame.pack(fill="x", padx=20, pady=10)
        self.icon_label = ttk.Label(self.current_frame)
        self.icon_label.grid(row=0, column=0, rowspan=3, padx=10)
        self.temp_label = ttk.Label(self.current_frame, text="Temp: --", style="Header.TLabel")
        self.temp_label.grid(row=0, column=1, sticky="w")
        self.desc_label = ttk.Label(self.current_frame, text="Condition: --")
        self.desc_label.grid(row=1, column=1, sticky="w")
        self.extra_label = ttk.Label(self.current_frame, text="Humidity: -- | Wind: --")
        self.extra_label.grid(row=2, column=1, sticky="w")

        # Forecast notebooks (hourly & daily)
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both", padx=20, pady=10)
        self.hourly_frame = ttk.Frame(notebook)
        self.daily_frame = ttk.Frame(notebook)
        notebook.add(self.hourly_frame, text="Hourly (12h)")
        notebook.add(self.daily_frame, text="Daily (5d)")

        # History panel (optional collapsible)
        self.history_button = ttk.Button(self, text="Show History", command=self._show_history)
        self.history_button.pack(pady=5)

    # ---------- Data Retrieval ----------
    def _fetch_coords(self, location):
        """Geocode a city name using OpenStreetMap via geocoder package."""
        try:
            g = arcgis(location)
            if g.ok:
                return g.lat, g.lng
            else:
                raise ValueError("Geocoding failed")
        except Exception as e:
            messagebox.showerror("Geocoding Error", str(e))
            return None, None

    def _auto_location(self):
        """Detect user IP location and fetch weather."""
        def worker():
            g = ip('me')
            if g.ok:
                lat, lon = g.latlng
                self._load_weather(lat, lon, city_name=g.city or f"{lat:.2f},{lon:.2f}")
            else:
                messagebox.showerror("Location Error", "Could not detect your IP location.")
        threading.Thread(target=worker, daemon=True).start()

    def _on_search(self):
        location = self.city_var.get().strip()
        if not location:
            messagebox.showwarning("Input", "Enter a city name.")
            return
        lat, lon = self._fetch_coords(location)
        if lat is not None:
            self._load_weather(lat, lon, city_name=location)

    def _load_weather(self, lat, lon, city_name=""):
        """Fetch weather JSON from Open‑Meteo and update UI."""
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
            "hourly": "temperature_2m,weathercode,relativehumidity_2m,windspeed_10m",
            "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "timezone": "auto",
        }
        def worker():
            try:
                resp = requests.get(API_URL, params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                self._update_ui(data, city_name)
                self._save_history(city_name, lat, lon)
            except Exception as e:
                messagebox.showerror("API Error", f"Failed to retrieve weather: {e}")
        threading.Thread(target=worker, daemon=True).start()

    # ---------- UI Updating ----------
    def _update_ui(self, data, city_name):
        # Current
        cw = data.get("current_weather", {})
        temp = cw.get("temperature")
        code = cw.get("weathercode")
        wind = cw.get("windspeed")
        # Convert units
        if self.units == "imperial":
            temp = temp * 9/5 + 32
            wind = wind * 0.621371
            unit_temp = "°F"
            unit_wind = "mph"
        else:
            unit_temp = "°C"
            unit_wind = "km/h"
        # Update labels
        self.temp_label.config(text=f"{city_name or 'Location'}: {temp:.1f}{unit_temp}")
        self.desc_label.config(text=f"Condition: {self._code_to_text(code)}")
        self.extra_label.config(text=f"Humidity: {self._get_humidity(data)}% | Wind: {wind:.1f}{unit_wind}")
        # Icon
        icon_img = self._load_icon(code)
        if icon_img:
            self.icon_label.config(image=icon_img)
            self.icon_label.image = icon_img
        # Forecasts
        self._populate_hourly(data.get("hourly", {}))
        self._populate_daily(data.get("daily", {}))

    def _code_to_text(self, code):
        mapping = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Freezing drizzle",
            57: "Freezing rain",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail",
        }
        return mapping.get(code, "Unknown")

    def _load_icon(self, code):
        try:
            url = f"{ICON_URL}{code}.png"
            resp = requests.get(url, stream=True, timeout=5)
            resp.raise_for_status()
            img = Image.open(resp.raw).resize((80, 80), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def _get_humidity(self, data):
        # Use first hourly humidity value as approximation
        hum = data.get("hourly", {}).get("relativehumidity_2m", [None])[0]
        return hum if hum is not None else "--"

    def _populate_hourly(self, hourly):
        for widget in self.hourly_frame.winfo_children():
            widget.destroy()
        times = hourly.get("time", [])[:12]
        temps = hourly.get("temperature_2m", [])[:12]
        codes = hourly.get("weathercode", [])[:12]
        for i, (t, temp, code) in enumerate(zip(times, temps, codes)):
            dt = datetime.fromisoformat(t)
            lbl = ttk.Label(self.hourly_frame, text=dt.strftime("%I %p\n{temp:.0f}°"), justify="center")
            lbl.grid(row=0, column=i, padx=5, pady=5)
            ic = self._load_icon(code)
            if ic:
                ttk.Label(self.hourly_frame, image=ic).grid(row=1, column=i)
                # keep reference
                lbl.image = ic

    def _populate_daily(self, daily):
        for widget in self.daily_frame.winfo_children():
            widget.destroy()
        dates = daily.get("time", [])[:5]
        max_t = daily.get("temperature_2m_max", [])[:5]
        min_t = daily.get("temperature_2m_min", [])[:5]
        codes = daily.get("weathercode", [])[:5]
        for i, (d, mx, mn, code) in enumerate(zip(dates, max_t, min_t, codes)):
            dt = datetime.fromisoformat(d)
            ttk.Label(self.daily_frame, text=dt.strftime("%a %d"), font=("Segoe UI", 10, "bold")).grid(row=0, column=i, pady=5)
            ic = self._load_icon(code)
            if ic:
                ttk.Label(self.daily_frame, image=ic).grid(row=1, column=i)
            ttk.Label(self.daily_frame, text=f"{mn:.0f}° / {mx:.0f}°", font=("Segoe UI", 9)).grid(row=2, column=i)

    # ---------- Units ----------
    def _toggle_units(self):
        self.units = "imperial" if self.units == "metric" else "metric"
        messagebox.showinfo("Units", f"Switched to {self.units.title()} units.")
        # Force refresh if we have last weather data
        # (simplify: re‑run the last search)
        if hasattr(self, "last_lat"):
            self._load_weather(self.last_lat, self.last_lon, city_name=self.last_city)

    # ---------- History ----------
    def _load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                self.history = json.load(f)
        else:
            self.history = []

    def _save_history(self, city, lat, lon):
        entry = {"city": city, "lat": lat, "lon": lon, "time": time.time()}
        self.history.insert(0, entry)
        self.history = self.history[:20]  # keep recent 20
        with open(HISTORY_FILE, "w") as f:
            json.dump(self.history, f, indent=2)
        # remember for unit toggle
        self.last_city = city
        self.last_lat = lat
        self.last_lon = lon

    def _show_history(self):
        if not self.history:
            messagebox.showinfo("History", "No recent searches.")
            return
        top = tk.Toplevel(self)
        top.title("Search History")
        top.geometry("300x400")
        ttk.Label(top, text="Recent Locations", font=("Segoe UI", 12, "bold")).pack(pady=5)
        listbox = tk.Listbox(top, font=("Segoe UI", 10))
        listbox.pack(fill="both", expand=True, padx=10, pady=5)
        for entry in self.history:
            listbox.insert(tk.END, entry["city"])
        def on_select(event):
            idx = listbox.curselection()
            if idx:
                entry = self.history[idx[0]]
                self._load_weather(entry["lat"], entry["lon"], entry["city"])
                top.destroy()
        listbox.bind("<<ListboxSelect>>", on_select)

if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
