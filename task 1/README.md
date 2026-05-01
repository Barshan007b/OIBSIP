# Smart BMI Tracker & Analyzer

A feature-rich desktop health-monitoring application built with Python, Tkinter, SQLite, and Matplotlib.

## Features
- Multi-user profile management (add / delete users)
- BMI calculation with live gauge meter
- Health category classification + personalised messages
- Full history table with colour-coded categories
- BMI trend line chart, category pie/donut chart, and stats bar chart
- Export history to CSV and save graphs as PNG images
- Live clock and dark-mode premium UI

## Project Structure
```
BMI_Project/
├── app.py          — Main GUI application (entry point)
├── bmi_engine.py   — BMI calculation, validation, categorisation
├── charts.py       — Matplotlib chart builders
├── database.py     — SQLite CRUD layer
├── export_utils.py — CSV / PNG export helpers
├── ui_theme.py     — Design tokens (colours, fonts, spacing)
├── requirements.txt
└── bmi_data.db     — Auto-created on first run
```

## Setup & Run

### Option A – pip
```bash
pip install -r requirements.txt
python app.py
```

### Option B – uv (faster)
```bash
uv pip install -r requirements.txt
python app.py
```

## Usage
1. **Add a user** in the left sidebar → type a name → click ➕ Add User
2. **Select the user** from the list
3. Go to the **Calculator** tab → enter Weight (kg) and Height (cm) → Calculate BMI
4. Click **💾 Save Record** to persist the result
5. View the **History** tab to browse all records and export to CSV
6. View the **Charts** tab for trend lines, pie distribution, and statistics
