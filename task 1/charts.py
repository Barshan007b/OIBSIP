"""
charts.py — Matplotlib chart builders for the BMI Tracker application.
All functions return (fig, ax) tuples that can be embedded in a Tkinter
FigureCanvasTkAgg widget or exported to PNG.
"""

from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import numpy as np

# Use a clean, modern style
plt.style.use("dark_background")

# ─── Colour palette ──────────────────────────────────────────────────────────
PALETTE = {
    "bg":         "#1A1A2E",
    "surface":    "#16213E",
    "accent":     "#7C4DFF",
    "accent2":    "#03DAC6",
    "text":       "#E0E0E0",
    "grid":       "#2D2D4E",
    "Underweight":"#4FC3F7",
    "Normal Weight":"#81C784",
    "Overweight": "#FFB74D",
    "Obese":      "#EF5350",
}

FIG_BG    = PALETTE["bg"]
AXES_BG   = PALETTE["surface"]
TEXT_COL  = PALETTE["text"]
GRID_COL  = PALETTE["grid"]


def _base_fig(figsize=(10, 4.5)):
    fig, ax = plt.subplots(figsize=figsize, facecolor=FIG_BG)
    ax.set_facecolor(AXES_BG)
    ax.tick_params(colors=TEXT_COL, labelsize=9)
    ax.xaxis.label.set_color(TEXT_COL)
    ax.yaxis.label.set_color(TEXT_COL)
    ax.title.set_color(TEXT_COL)
    for spine in ax.spines.values():
        spine.set_color(GRID_COL)
    ax.grid(color=GRID_COL, linestyle="--", linewidth=0.5, alpha=0.7)
    return fig, ax


# ─── 1. BMI Trend Line Chart ─────────────────────────────────────────────────

def build_trend_chart(records: list[dict]) -> tuple:
    """
    Line chart of BMI over time.
    records: list of dicts with keys 'recorded_at', 'bmi', 'category'
    """
    fig, ax = _base_fig(figsize=(10, 4.5))

    if not records:
        ax.text(0.5, 0.5, "No records yet.\nAdd a BMI entry to see your trend.",
                ha="center", va="center", color=TEXT_COL, fontsize=13,
                transform=ax.transAxes)
        ax.set_title("BMI Trend Over Time", fontsize=14, fontweight="bold", pad=12)
        return fig, ax

    # Parse dates (records come newest-first → reverse for chronological order)
    data = list(reversed(records))
    dates = [datetime.fromisoformat(r["recorded_at"]) for r in data]
    bmis  = [r["bmi"] for r in data]
    cats  = [r["category"] for r in data]

    # Shaded BMI zones
    xmin, xmax = dates[0], dates[-1]
    ax.axhspan(0,    18.5, color=PALETTE["Underweight"],  alpha=0.08)
    ax.axhspan(18.5, 25,   color=PALETTE["Normal Weight"],alpha=0.08)
    ax.axhspan(25,   30,   color=PALETTE["Overweight"],   alpha=0.08)
    ax.axhspan(30,   60,   color=PALETTE["Obese"],        alpha=0.08)

    # Reference lines
    for val, label in [(18.5, "18.5"), (25, "25"), (30, "30")]:
        ax.axhline(val, color=GRID_COL, linewidth=0.8, linestyle="--")
        ax.text(dates[0], val + 0.3, label, color=TEXT_COL, fontsize=7, alpha=0.7)

    # Gradient fill under curve
    ax.fill_between(dates, bmis, alpha=0.15, color=PALETTE["accent"])

    # Main line
    ax.plot(dates, bmis, color=PALETTE["accent"], linewidth=2.5,
            marker="o", markersize=6, markerfacecolor=PALETTE["accent2"],
            markeredgecolor="white", markeredgewidth=1.2, zorder=5)

    # Colour each point by category
    for d, b, c in zip(dates, bmis, cats):
        ax.scatter(d, b, color=PALETTE.get(c, PALETTE["accent"]),
                   s=60, zorder=6, edgecolors="white", linewidths=0.8)

    # Annotate latest value
    ax.annotate(
        f"Latest: {bmis[-1]}",
        xy=(dates[-1], bmis[-1]),
        xytext=(10, 10), textcoords="offset points",
        color=PALETTE["accent2"], fontsize=9, fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=PALETTE["accent2"], lw=1.2),
    )

    ax.set_title("BMI Trend Over Time", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("BMI", fontsize=10)

    # Smart date formatting
    locator   = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    fig.autofmt_xdate(rotation=30)

    # Legend for zones
    legend_patches = [
        mpatches.Patch(color=PALETTE[c], label=c, alpha=0.6)
        for c in ["Underweight", "Normal Weight", "Overweight", "Obese"]
    ]
    ax.legend(handles=legend_patches, loc="upper left",
              facecolor=AXES_BG, edgecolor=GRID_COL,
              labelcolor=TEXT_COL, fontsize=8)

    fig.tight_layout()
    return fig, ax


# ─── 2. Category Distribution Pie Chart ──────────────────────────────────────

def build_category_pie(records: list[dict]) -> tuple:
    """Pie / donut chart showing distribution across BMI categories."""
    fig, ax = plt.subplots(figsize=(5, 4.5), facecolor=FIG_BG,
                           subplot_kw=dict(aspect="equal"))
    ax.set_facecolor(AXES_BG)

    if not records:
        ax.text(0.5, 0.5, "No data", ha="center", va="center",
                color=TEXT_COL, fontsize=13, transform=ax.transAxes)
        ax.set_title("Category Distribution", fontsize=13, fontweight="bold",
                     color=TEXT_COL)
        return fig, ax

    from collections import Counter
    counts = Counter(r["category"] for r in records)
    cat_order = ["Underweight", "Normal Weight", "Overweight", "Obese"]
    labels  = [c for c in cat_order if c in counts]
    sizes   = [counts[c] for c in labels]
    colors  = [PALETTE[c] for c in labels]

    wedges, texts, autotexts = ax.pie(
        sizes, labels=None, colors=colors,
        autopct="%1.0f%%", startangle=90,
        pctdistance=0.78,
        wedgeprops=dict(width=0.55, edgecolor=FIG_BG, linewidth=2),
    )
    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(9)
        at.set_fontweight("bold")

    ax.legend(wedges, labels, loc="lower center", bbox_to_anchor=(0.5, -0.12),
              ncol=2, facecolor=AXES_BG, edgecolor=GRID_COL,
              labelcolor=TEXT_COL, fontsize=8)
    ax.set_title("Category Distribution", fontsize=13, fontweight="bold",
                 color=TEXT_COL, pad=10)

    fig.tight_layout()
    return fig, ax


# ─── 3. Stats Bar Chart ───────────────────────────────────────────────────────

def build_stats_bar(stats: dict) -> tuple:
    """Horizontal bar chart for Avg / Min / Max BMI."""
    fig, ax = _base_fig(figsize=(5, 2.8))
    ax.set_facecolor(AXES_BG)

    if not stats or stats.get("total", 0) == 0:
        ax.text(0.5, 0.5, "No stats available", ha="center", va="center",
                color=TEXT_COL, transform=ax.transAxes)
        return fig, ax

    labels = ["Min BMI", "Avg BMI", "Max BMI"]
    values = [stats["min_bmi"], stats["avg_bmi"], stats["max_bmi"]]
    colors = [PALETTE["Normal Weight"], PALETTE["accent"], PALETTE["Overweight"]]

    bars = ax.barh(labels, values, color=colors, height=0.45,
                   edgecolor="white", linewidth=0.5)
    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}", va="center", color=TEXT_COL, fontsize=10,
                fontweight="bold")

    ax.set_xlim(0, max(values) * 1.25)
    ax.set_xlabel("BMI Value", fontsize=9)
    ax.set_title("BMI Statistics", fontsize=12, fontweight="bold", pad=8)
    fig.tight_layout()
    return fig, ax
