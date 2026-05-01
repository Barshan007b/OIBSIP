"""
export_utils.py — CSV and graph-image export helpers.
"""

import csv
import os
from datetime import datetime
from tkinter import filedialog, messagebox

import matplotlib
matplotlib.use("Agg")          # off-screen rendering for export
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch


def export_to_csv(records: list[dict], username: str):
    """Prompt the user for a save path and write records to CSV."""
    if not records:
        messagebox.showwarning("No Data", "No records to export.")
        return

    default_name = f"{username}_bmi_history_{datetime.now().strftime('%Y%m%d')}.csv"
    path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        initialfile=default_name,
        title="Export BMI History as CSV",
    )
    if not path:
        return

    fieldnames = ["Date & Time", "Weight (kg)", "Height (cm)", "BMI", "Category"]
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in records:
                writer.writerow({
                    "Date & Time":  r["recorded_at"],
                    "Weight (kg)":  r["weight_kg"],
                    "Height (cm)":  r["height_cm"],
                    "BMI":          r["bmi"],
                    "Category":     r["category"],
                })
        messagebox.showinfo("Exported", f"Data saved to:\n{path}")
    except OSError as e:
        messagebox.showerror("Export Failed", str(e))


def export_graph_image(fig: "plt.Figure"):
    """Prompt the user for a save path and write the given figure to PNG."""
    path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
        title="Save Graph as Image",
    )
    if not path:
        return
    try:
        fig.savefig(path, dpi=150, bbox_inches="tight")
        messagebox.showinfo("Saved", f"Graph saved to:\n{path}")
    except OSError as e:
        messagebox.showerror("Save Failed", str(e))
