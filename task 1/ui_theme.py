"""
ui_theme.py — Design tokens and reusable widget factories.
"""

# ─── Colours ──────────────────────────────────────────────────────────────────
BG_DARK     = "#0F0F1A"
BG_SURFACE  = "#1A1A2E"
BG_CARD     = "#16213E"
BG_INPUT    = "#0D1B2A"
ACCENT      = "#7C4DFF"
ACCENT_LIGHT= "#A87FFF"
ACCENT2     = "#03DAC6"
TEXT_PRI    = "#FFFFFF"
TEXT_SEC    = "#B0B8C1"
TEXT_DIM    = "#6B7A8D"
BORDER      = "#2D2D4E"
SUCCESS     = "#81C784"
WARNING     = "#FFB74D"
DANGER      = "#EF5350"
INFO        = "#4FC3F7"

# BMI category colours
CAT_COLORS = {
    "Underweight":  INFO,
    "Normal Weight":SUCCESS,
    "Overweight":   WARNING,
    "Obese":        DANGER,
}

# ─── Fonts ───────────────────────────────────────────────────────────────────
FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_HEAD   = ("Segoe UI", 14, "bold")
FONT_SUBHEAD= ("Segoe UI", 11, "bold")
FONT_BODY   = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 9)
FONT_MONO   = ("Consolas", 10)
FONT_NUM    = ("Segoe UI", 36, "bold")
FONT_BIG    = ("Segoe UI", 18, "bold")

# ─── Dimensions ──────────────────────────────────────────────────────────────
PAD         = 14
PAD_SM      = 7
RADIUS      = 10
ENTRY_H     = 38
BTN_H       = 40
