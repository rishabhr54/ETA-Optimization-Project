"""
Dashboard Configuration
Centralized config for paths, theme colors, and constants.
"""

import os

# ─── Data Paths ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "cleaned")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

GRAPH_FEATURED_DATA = os.path.join(DATA_DIR, "graph_featured_data.csv")
GRAPH_DATA = os.path.join(DATA_DIR, "graph_data.csv")
MODEL_COMPARISON = os.path.join(REPORTS_DIR, "model_comparison.csv")

# ─── Theme Colors ──────────────────────────────────────────────────────────────
COLORS = {
    "primary": "#6366F1",        # Indigo
    "primary_light": "#818CF8",
    "secondary": "#EC4899",      # Pink
    "accent": "#14B8A6",         # Teal
    "success": "#22C55E",        # Green
    "warning": "#F59E0B",        # Amber
    "danger": "#EF4444",         # Red
    "info": "#3B82F6",           # Blue
    "bg_dark": "#0F172A",        # Slate 900
    "bg_card": "#1E293B",        # Slate 800
    "text_primary": "#F1F5F9",   # Slate 100
    "text_muted": "#94A3B8",     # Slate 400
    "border": "#334155",         # Slate 700
}

# Plotly color scales
DELAY_COLORSCALE = [
    [0.0, "#22C55E"],   # Green - low delay
    [0.3, "#F59E0B"],   # Amber - moderate
    [0.6, "#F97316"],   # Orange - high
    [1.0, "#EF4444"],   # Red - critical
]

GRADIENT_COLORS = ["#6366F1", "#818CF8", "#A78BFA", "#C4B5FD", "#DDD6FE"]

CHART_COLORS = [
    "#6366F1", "#EC4899", "#14B8A6", "#F59E0B", "#3B82F6",
    "#8B5CF6", "#EF4444", "#22C55E", "#06B6D4", "#F97316",
]

# ─── Dashboard Constants ───────────────────────────────────────────────────────
SLA_THRESHOLD = 1.5         # delay_ratio above this = SLA breach
BOTTLENECK_THRESHOLD = 0.7  # top 30% centrality = bottleneck
HIGH_RISK_SCORE = 3.0       # corridor risk score threshold
TOP_N = 15                  # default top-N for charts

# ─── Plotly Layout Defaults ────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=COLORS["text_primary"]),
    margin=dict(l=40, r=20, t=50, b=40),
    hoverlabel=dict(
        bgcolor=COLORS["bg_card"],
        font_size=13,
        font_family="Inter, sans-serif",
        bordercolor=COLORS["border"],
    ),
)
