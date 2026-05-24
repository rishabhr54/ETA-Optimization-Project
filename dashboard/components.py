"""
UI Components Module
Reusable Streamlit UI components and CSS — Delhivery-inspired theme.
White background, black sidebar, red accents. Clean and corporate.
"""

import streamlit as st
from config import COLORS


def inject_custom_css():
    """Inject the Delhivery-themed CSS for the entire dashboard."""
    st.markdown("""
    <style>
    /* ─── Google Font ─────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ─── Reset & Global ──────────────────────────────────────────── */
    html, body, [class*="st-"] {
        font-family: 'Inter', Arial, sans-serif;
    }

    /* Page background — clean light gray */
    .stApp {
        background-color: #F5F5F5;
    }

    /* ─── Sidebar — dark/black Delhivery style ────────────────────── */
    section[data-testid="stSidebar"] {
        background-color: #1C1C1E;
        border-right: 3px solid #D0021B;
    }
    section[data-testid="stSidebar"] * {
        color: #F9FAFB !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stRadio label {
        color: #9CA3AF !important;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 600;
    }
    /* Sidebar radio buttons */
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        font-size: 13px !important;
        font-weight: 500 !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        padding: 6px 8px;
        border-radius: 6px;
        transition: background 0.15s;
    }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background: rgba(208, 2, 27, 0.12);
    }
    /* Sidebar inputs */
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background: #2C2C2E;
        border: 1px solid #3A3A3C;
        color: #F9FAFB;
        border-radius: 6px;
    }
    section[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] {
        margin-top: 4px;
    }
    /* Sidebar slider accent color */
    section[data-testid="stSidebar"] [data-testid="stSlider"] [data-baseweb="thumb"] {
        background: #D0021B !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSlider"] [data-baseweb="track-fill"] {
        background: #D0021B !important;
    }

    /* ─── Main content area ───────────────────────────────────────── */
    .main .block-container {
        padding: 2rem 2.5rem 3rem 2.5rem;
        max-width: 1400px;
    }

    /* ─── KPI Cards ──────────────────────────────────────────────── */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-top: 3px solid var(--accent-color, #D0021B);
        border-radius: 8px;
        padding: 20px 18px 16px 18px;
        text-align: left;
        transition: box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    }
    .kpi-icon {
        font-size: 22px;
        margin-bottom: 8px;
        display: block;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 800;
        color: #1C1C1E;
        line-height: 1.1;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }
    .kpi-label {
        font-size: 11px;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .kpi-delta {
        font-size: 12px;
        font-weight: 600;
        margin-top: 6px;
        display: flex;
        align-items: center;
        gap: 3px;
    }
    .kpi-delta.positive { color: #15803D; }
    .kpi-delta.negative { color: #B91C1C; }

    /* ─── Section Headers ────────────────────────────────────────── */
    .section-header {
        font-size: 16px;
        font-weight: 700;
        color: #1C1C1E;
        margin: 28px 0 4px 0;
        display: flex;
        align-items: center;
        gap: 8px;
        letter-spacing: -0.2px;
    }
    .section-header::after {
        content: '';
        display: inline-block;
        height: 2px;
        flex: 1;
        background: #E5E7EB;
        margin-left: 8px;
        border-radius: 1px;
    }
    .section-subtitle {
        font-size: 13px;
        color: #6B7280;
        margin-bottom: 16px;
        line-height: 1.5;
        font-weight: 400;
    }

    /* ─── Insight / Alert Boxes ──────────────────────────────────── */
    .insight-box {
        background: #F9FAFB;
        border-left: 3px solid #D0021B;
        border-radius: 0 6px 6px 0;
        padding: 14px 16px;
        margin: 10px 0;
        color: #374151;
        font-size: 13px;
        line-height: 1.6;
        border: 1px solid #E5E7EB;
        border-left: 3px solid #D0021B;
    }
    .insight-box strong { color: #1C1C1E; }

    .warning-box {
        background: #FFFBEB;
        border-left: 3px solid #B45309;
        border-radius: 0 6px 6px 0;
        padding: 14px 16px;
        margin: 10px 0;
        color: #374151;
        font-size: 13px;
        line-height: 1.6;
        border: 1px solid #FDE68A;
        border-left: 3px solid #B45309;
    }
    .danger-box {
        background: #FEF2F2;
        border-left: 3px solid #B91C1C;
        border-radius: 0 6px 6px 0;
        padding: 14px 16px;
        margin: 10px 0;
        color: #374151;
        font-size: 13px;
        line-height: 1.6;
        border: 1px solid #FECACA;
        border-left: 3px solid #B91C1C;
    }
    .success-box {
        background: #F0FDF4;
        border-left: 3px solid #15803D;
        border-radius: 0 6px 6px 0;
        padding: 14px 16px;
        margin: 10px 0;
        color: #374151;
        font-size: 13px;
        line-height: 1.6;
        border: 1px solid #BBF7D0;
        border-left: 3px solid #15803D;
    }

    /* ─── Page Title ─────────────────────────────────────────────── */
    .page-title {
        font-size: 28px;
        font-weight: 800;
        color: #1C1C1E;
        margin-bottom: 2px;
        letter-spacing: -0.5px;
        line-height: 1.2;
    }
    .page-title-accent {
        color: #D0021B;
    }
    .page-subtitle {
        font-size: 14px;
        color: #6B7280;
        margin-bottom: 24px;
        font-weight: 400;
    }

    /* ─── Divider ────────────────────────────────────────────────── */
    .custom-divider {
        height: 1px;
        background: #E5E7EB;
        margin: 20px 0;
        border: none;
    }

    /* ─── Nav badge ──────────────────────────────────────────────── */
    .nav-badge {
        display: inline-block;
        background: #FEE2E2;
        color: #B91C1C;
        padding: 2px 10px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    /* ─── Streamlit metric overrides ─────────────────────────────── */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 16px;
    }

    /* ─── DataFrame ──────────────────────────────────────────────── */
    .stDataFrame {
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        overflow: hidden;
    }

    /* ─── Buttons ────────────────────────────────────────────────── */
    .stDownloadButton > button {
        background: #D0021B;
        color: #FFFFFF;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        font-size: 13px;
        padding: 8px 20px;
        transition: background 0.15s;
    }
    .stDownloadButton > button:hover {
        background: #A30015;
    }

    /* ─── Top header bar ─────────────────────────────────────────── */
    header[data-testid="stHeader"] {
        background: #FFFFFF;
        border-bottom: 1px solid #E5E7EB;
    }

    /* ─── Plotly chart container ──────────────────────────────────── */
    .stPlotlyChart {
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        background: #FFFFFF;
        overflow: hidden;
    }

    /* ─── Expander ───────────────────────────────────────────────── */
    .streamlit-expanderHeader {
        background: #F9FAFB;
        border-radius: 6px;
        font-weight: 600;
        font-size: 13px;
        color: #1C1C1E;
    }

    /* ─── Scrollbar ──────────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #F5F5F5; }
    ::-webkit-scrollbar-thumb {
        background: #D1D5DB;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: #9CA3AF; }

    /* ─── Hide default Streamlit chrome ──────────────────────────── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)


def render_kpi_card(icon: str, value: str, label: str,
                    accent_color: str = "#D0021B",
                    delta: str = None, delta_positive: bool = True):
    """Render a clean, corporate KPI card."""
    delta_html = ""
    if delta:
        cls = "positive" if delta_positive else "negative"
        arrow = "↑" if delta_positive else "↓"
        delta_html = f'<div class="kpi-delta {cls}">{arrow} {delta}</div>'

    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: {accent_color};">
        <span class="kpi-icon">{icon}</span>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_section_header(icon: str, title: str, subtitle: str = ""):
    """Render a section header with horizontal rule."""
    st.markdown(f'<div class="section-header">{icon} {title}</div>',
                unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-subtitle">{subtitle}</div>',
                    unsafe_allow_html=True)


def render_insight(text: str, box_type: str = "insight"):
    """Render an insight/alert box."""
    st.markdown(f'<div class="{box_type}-box">{text}</div>',
                unsafe_allow_html=True)


def render_divider():
    """Render a subtle hairline divider."""
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str = ""):
    """Render a page-level header."""
    # Split title at first space to accent the first word in red
    parts = title.split(" ", 1)
    first = parts[0]
    rest = f" {parts[1]}" if len(parts) > 1 else ""
    st.markdown(
        f'<div class="page-title">'
        f'<span class="page-title-accent">{first}</span>{rest}'
        f'</div>',
        unsafe_allow_html=True
    )
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>',
                    unsafe_allow_html=True)
