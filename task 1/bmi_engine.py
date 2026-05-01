"""
bmi_engine.py — Pure-logic module for BMI calculations, categorisation,
validation, and health messaging.
"""

from dataclasses import dataclass


# ─── Constants ────────────────────────────────────────────────────────────────

WEIGHT_MIN_KG  = 10.0
WEIGHT_MAX_KG  = 500.0
HEIGHT_MIN_CM  = 50.0
HEIGHT_MAX_CM  = 300.0

CATEGORIES = [
    (0,    18.5, "Underweight",    "#4FC3F7"),
    (18.5, 25.0, "Normal Weight",  "#81C784"),
    (25.0, 30.0, "Overweight",     "#FFB74D"),
    (30.0, float("inf"), "Obese",  "#EF5350"),
]

HEALTH_MESSAGES = {
    "Underweight":   (
        "You are below a healthy weight range.\n"
        "Consider consulting a nutritionist to build a balanced diet plan."
    ),
    "Normal Weight": (
        "Great job! You are within a healthy weight range.\n"
        "Keep maintaining your balanced diet and regular exercise."
    ),
    "Overweight":    (
        "You are slightly above a healthy weight range.\n"
        "Regular physical activity and a mindful diet can help."
    ),
    "Obese":         (
        "Your BMI indicates obesity, which can raise health risks.\n"
        "Please consult a healthcare professional for personalised guidance."
    ),
}


# ─── Data class ───────────────────────────────────────────────────────────────

@dataclass
class BMIResult:
    bmi: float
    category: str
    color: str
    message: str
    weight_kg: float
    height_cm: float


# ─── Public API ───────────────────────────────────────────────────────────────

def validate_inputs(weight_str: str, height_str: str) -> tuple[float, float]:
    """
    Parse and validate weight and height strings.

    Returns (weight_kg, height_cm) on success.
    Raises ValueError with a descriptive message on any problem.
    """
    # --- weight ---
    try:
        weight = float(weight_str)
    except (ValueError, TypeError):
        raise ValueError("Weight must be a valid number (e.g. 70.5).")

    if weight <= 0:
        raise ValueError("Weight must be greater than zero.")
    if not (WEIGHT_MIN_KG <= weight <= WEIGHT_MAX_KG):
        raise ValueError(
            f"Weight must be between {WEIGHT_MIN_KG:.0f} kg and {WEIGHT_MAX_KG:.0f} kg."
        )

    # --- height ---
    try:
        height = float(height_str)
    except (ValueError, TypeError):
        raise ValueError("Height must be a valid number (e.g. 170).")

    if height <= 0:
        raise ValueError("Height cannot be zero or negative.")
    if not (HEIGHT_MIN_CM <= height <= HEIGHT_MAX_CM):
        raise ValueError(
            f"Height must be between {HEIGHT_MIN_CM:.0f} cm and {HEIGHT_MAX_CM:.0f} cm."
        )

    return weight, height


def calculate_bmi(weight_kg: float, height_cm: float) -> BMIResult:
    """Calculate BMI and return a fully populated BMIResult."""
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m ** 2)
    bmi = round(bmi, 2)

    category, color = _classify(bmi)
    message = HEALTH_MESSAGES[category]

    return BMIResult(
        bmi=bmi,
        category=category,
        color=color,
        message=message,
        weight_kg=weight_kg,
        height_cm=height_cm,
    )


def category_color(category: str) -> str:
    """Return the hex colour associated with a BMI category."""
    for _, _, cat, col in CATEGORIES:
        if cat == category:
            return col
    return "#FFFFFF"


def bmi_meter_fraction(bmi: float) -> float:
    """
    Map a BMI value to a fraction 0‑1 for the animated gauge.
    We cap the visible range at 10–40.
    """
    low, high = 10.0, 40.0
    return max(0.0, min(1.0, (bmi - low) / (high - low)))


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _classify(bmi: float) -> tuple[str, str]:
    for lo, hi, category, color in CATEGORIES:
        if lo <= bmi < hi:
            return category, color
    return CATEGORIES[-1][2], CATEGORIES[-1][3]
