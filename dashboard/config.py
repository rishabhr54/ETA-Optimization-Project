"""
Dashboard Configuration
Centralized config for paths, theme colors, and constants.
Theme: Delhivery-inspired — white, black, and red; clean and corporate.
"""

import os

# ─── Data Paths ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "cleaned")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

GRAPH_FEATURED_DATA = os.path.join(DATA_DIR, "graph_featured_data.csv")
GRAPH_DATA = os.path.join(DATA_DIR, "graph_data.csv")
MODEL_COMPARISON = os.path.join(REPORTS_DIR, "model_comparison.csv")

# ─── Theme Colors (Delhivery palette) ─────────────────────────────────────────
COLORS = {
    "primary":       "#D0021B",   # Delhivery red
    "primary_light": "#F4CDD1",   # Light red tint
    "primary_dark":  "#A30015",   # Deep red
    "secondary":     "#1C1C1E",   # Near-black
    "accent":        "#374151",   # Dark slate (secondary text/icons)
    "success":       "#15803D",   # Muted green
    "warning":       "#B45309",   # Muted amber
    "danger":        "#B91C1C",   # Muted red (distinct from primary)
    "info":          "#1D4ED8",   # Muted blue
    "bg_page":       "#F5F5F5",   # Light gray page background
    "bg_card":       "#FFFFFF",   # White card
    "bg_sidebar":    "#1C1C1E",   # Dark sidebar (contrast)
    "text_primary":  "#1C1C1E",   # Near-black body text
    "text_muted":    "#6B7280",   # Medium gray
    "text_light":    "#9CA3AF",   # Light gray
    "border":        "#E5E7EB",   # Hairline border
    "border_dark":   "#D1D5DB",   # Slightly darker border
}

# Plotly color scales — subdued, red-anchored
DELAY_COLORSCALE = [
    [0.0, "#22C55E"],   # Green — on time
    [0.4, "#F59E0B"],   # Amber — moderate
    [0.7, "#F97316"],   # Orange — high
    [1.0, "#B91C1C"],   # Dark red — critical
]

GRADIENT_COLORS = ["#D0021B", "#E04D5A", "#E87A84", "#F0A8AE", "#F7D5D8"]

CHART_COLORS = [
    "#D0021B",  # Red (primary)
    "#1C1C1E",  # Near-black
    "#374151",  # Slate
    "#B45309",  # Amber
    "#1D4ED8",  # Blue
    "#15803D",  # Green
    "#6B7280",  # Gray
    "#7C3AED",  # Violet (muted)
    "#0E7490",  # Cyan (muted)
    "#92400E",  # Brown
]

# ─── Dashboard Constants ───────────────────────────────────────────────────────
SLA_THRESHOLD = 1.5
BOTTLENECK_THRESHOLD = 0.7
HIGH_RISK_SCORE = 3.0
TOP_N = 15

# ─── Plotly Layout Defaults (light theme) ─────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(family="Inter, Arial, sans-serif", color=COLORS["text_primary"], size=12),
    margin=dict(l=48, r=24, t=56, b=48),
    hoverlabel=dict(
        bgcolor=COLORS["secondary"],
        font_size=12,
        font_family="Inter, Arial, sans-serif",
        font_color="#FFFFFF",
        bordercolor=COLORS["secondary"],
    ),
)
