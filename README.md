# OIBSIP - Oasis Infobyte Internship Projects

This repository contains the tasks completed during the Oasis Infobyte internship. Each task is organized into its own subfolder.

## 📁 Repository Structure

- **[task 2/](./task%202/)**: Secure Password Generator Pro
- **[TASK 3/](./TASK%203/)**: Smart Weather Forecast Application

---

## 🔐 Task 2: Secure Password Generator Pro

A powerful, high-security password generator with a premium dark-mode GUI.

### Key Features:
- **Cryptographic Security**: Uses the `secrets` module for truly random passwords.
- **Customization**: Toggle between Uppercase, Lowercase, Digits, and Symbols.
- **Length Control**: Support for password lengths from 4 to 128 characters.
- **Strength Analysis**: Real-time entropy calculation and visual strength meter.
- **Advanced Rules**: Options to avoid ambiguous characters (O, 0, l, I) and repeated characters.
- **History Management**: Automatically saves the last 50 generated passwords (persisted locally).
- **Clipboard Integration**: One-click copying with success notifications.
- **Exporting**: Export your password history to TXT or CSV files.

### 🚀 How to Run:
1. Navigate to the `task 2` folder.
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python password_generator.py`

---

## 🌤 Task 3: Smart Weather Forecast Application

A modern weather dashboard providing real-time data and long-term forecasts.

### Key Features:
- **Live Data**: Fetches data from the Open-Meteo API (no API key required).
- **Dual Location Support**: 
    - **Search**: Accurate city search using ArcGIS Geocoding.
    - **Auto-Detect**: IP-based location detection on startup.
- **Detailed Metrics**: Current temperature, weather conditions, humidity, and wind speed.
- **Comprehensive Forecasts**:
    - **Hourly**: 12-hour breakdown of temperature and conditions.
    - **Daily**: 5-day high/low temperature predictions.
- **Unit Toggling**: Switch between Metric (°C/km/h) and Imperial (°F/mph) systems.
- **History**: Keeps track of recently searched locations for quick access.
- **Visuals**: Dynamic weather icons and high-DPI scaled GUI.

### 🚀 How to Run:
1. Navigate to the `TASK 3` folder.
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python weather_app.py`

---

## 🛠 Technology Stack
- **Language**: Python 3.x
- **GUI**: Tkinter (with custom styling)
- **API Communication**: Requests
- **Image Processing**: Pillow (PIL)
- **Geocoding**: Geocoder (ArcGIS/IP)
- **Utilities**: Pyperclip, JSON, CSV

---
Created by Antigravity AI assistant for Oasis Infobyte Internship tasks.
