"""
UI Components Module
Reusable Streamlit UI components: KPI cards, charts, styling.
"""

import streamlit as st
from config import COLORS


def inject_custom_css():
    """Inject modern, premium custom CSS for the entire dashboard."""
    st.markdown("""
    <style>
    /* ─── Google Font ────────────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ─── Global ─────────────────────────────────────────────────────────── */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0F172A 0%, #1a1f3a 50%, #0F172A 100%);
    }

    /* ─── Sidebar ────────────────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
        border-right: 1px solid rgba(99,102,241,0.2);
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #F1F5F9;
    }

    /* ─── KPI Cards ──────────────────────────────────────────────────────── */
    .kpi-card {
        background: linear-gradient(145deg, #1E293B, #253348);
        border: 1px solid rgba(99,102,241,0.15);
        border-radius: 16px;
        padding: 24px 20px 20px 20px;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--accent-color, #6366F1), transparent);
        border-radius: 16px 16px 0 0;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(99,102,241,0.15);
        border-color: rgba(99,102,241,0.3);
    }
    .kpi-icon {
        font-size: 28px;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 32px;
        font-weight: 800;
        background: linear-gradient(135deg, #F1F5F9, #CBD5E1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
        margin-bottom: 4px;
    }
    .kpi-label {
        font-size: 12px;
        font-weight: 500;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }
    .kpi-delta {
        font-size: 13px;
        font-weight: 600;
        margin-top: 6px;
    }
    .kpi-delta.positive { color: #22C55E; }
    .kpi-delta.negative { color: #EF4444; }

    /* ─── Section Headers ────────────────────────────────────────────────── */
    .section-header {
        font-size: 22px;
        font-weight: 700;
        color: #F1F5F9;
        margin: 32px 0 8px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-subtitle {
        font-size: 14px;
        color: #94A3B8;
        margin-bottom: 20px;
        line-height: 1.5;
    }

    /* ─── Glass Card ─────────────────────────────────────────────────────── */
    .glass-card {
        background: rgba(30,41,59,0.7);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(99,102,241,0.12);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
    }

    /* ─── Insight Box ────────────────────────────────────────────────────── */
    .insight-box {
        background: linear-gradient(145deg, rgba(99,102,241,0.08), rgba(99,102,241,0.02));
        border-left: 3px solid #6366F1;
        border-radius: 0 12px 12px 0;
        padding: 16px 20px;
        margin: 12px 0;
        color: #CBD5E1;
        font-size: 14px;
        line-height: 1.6;
    }
    .insight-box strong {
        color: #F1F5F9;
    }

    /* ─── Warning / Danger Boxes ─────────────────────────────────────────── */
    .warning-box {
        background: linear-gradient(145deg, rgba(245,158,11,0.08), rgba(245,158,11,0.02));
        border-left: 3px solid #F59E0B;
        border-radius: 0 12px 12px 0;
        padding: 16px 20px;
        margin: 12px 0;
        color: #CBD5E1;
        font-size: 14px;
    }
    .danger-box {
        background: linear-gradient(145deg, rgba(239,68,68,0.08), rgba(239,68,68,0.02));
        border-left: 3px solid #EF4444;
        border-radius: 0 12px 12px 0;
        padding: 16px 20px;
        margin: 12px 0;
        color: #CBD5E1;
        font-size: 14px;
    }
    .success-box {
        background: linear-gradient(145deg, rgba(34,197,94,0.08), rgba(34,197,94,0.02));
        border-left: 3px solid #22C55E;
        border-radius: 0 12px 12px 0;
        padding: 16px 20px;
        margin: 12px 0;
        color: #CBD5E1;
        font-size: 14px;
    }

    /* ─── Navigation Pill ────────────────────────────────────────────────── */
    .nav-badge {
        display: inline-block;
        background: rgba(99,102,241,0.15);
        color: #818CF8;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    /* ─── Table styling ──────────────────────────────────────────────────── */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* ─── Metric override ────────────────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #1E293B, #253348);
        border: 1px solid rgba(99,102,241,0.12);
        border-radius: 12px;
        padding: 16px;
    }
    [data-testid="stMetricValue"] {
        font-weight: 700;
    }

    /* ─── Expander ───────────────────────────────────────────────────────── */
    .streamlit-expanderHeader {
        background: rgba(30,41,59,0.5);
        border-radius: 8px;
        font-weight: 600;
    }

    /* ─── Plotly chart container ──────────────────────────────────────────── */
    .stPlotlyChart {
        border-radius: 12px;
        overflow: hidden;
    }

    /* ─── Page title ─────────────────────────────────────────────────────── */
    .page-title {
        font-size: 36px;
        font-weight: 800;
        background: linear-gradient(135deg, #6366F1 0%, #EC4899 50%, #14B8A6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
        line-height: 1.3;
    }
    .page-subtitle {
        font-size: 16px;
        color: #94A3B8;
        margin-bottom: 30px;
        font-weight: 400;
    }

    /* ─── Divider ────────────────────────────────────────────────────────── */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(99,102,241,0.3), transparent);
        margin: 24px 0;
        border: none;
    }

    /* ─── Scrollbar ──────────────────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(99,102,241,0.3);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(99,102,241,0.5);
    }

    /* ─── Hide Streamlit defaults ────────────────────────────────────────── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] {
        background: rgba(15,23,42,0.8);
        backdrop-filter: blur(10px);
    }
    </style>
    """, unsafe_allow_html=True)


def render_kpi_card(icon: str, value: str, label: str, accent_color: str = "#6366F1", delta: str = None, delta_positive: bool = True):
    """Render a premium KPI metric card."""
    delta_html = ""
    if delta:
        cls = "positive" if delta_positive else "negative"
        arrow = "↑" if delta_positive else "↓"
        delta_html = f'<div class="kpi-delta {cls}">{arrow} {delta}</div>'

    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: {accent_color};">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_section_header(icon: str, title: str, subtitle: str = ""):
    """Render a styled section header."""
    st.markdown(f'<div class="section-header">{icon} {title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def render_insight(text: str, box_type: str = "insight"):
    """Render an insight / info box."""
    css_class = f"{box_type}-box"
    st.markdown(f'<div class="{css_class}">{text}</div>', unsafe_allow_html=True)


def render_divider():
    """Render a subtle gradient divider."""
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str = ""):
    """Render a page-level header with gradient title."""
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def render_glass_card_start():
    """Open a glass card container (use with markdown)."""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)


def render_glass_card_end():
    """Close a glass card container."""
    st.markdown('</div>', unsafe_allow_html=True)
