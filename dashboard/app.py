"""
ETA Optimization Dashboard — Main Application
───────────────────────────────────────────────
A professional logistics intelligence dashboard for monitoring,
analyzing, and optimizing Estimated Time of Arrival (ETA) across
a hub-and-spoke delivery network.

Built with Streamlit + Plotly + NetworkX

Author: ETA Optimization Team
"""

import sys
import os
import time

# Ensure the dashboard directory is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

# Monkeypatch st.plotly_chart to disable the Streamlit theme by default.
# This prevents Streamlit's dark mode from forcing chart text to white on our white backgrounds.
_original_plotly_chart = st.plotly_chart
def custom_plotly_chart(fig, *args, **kwargs):
    if 'theme' not in kwargs:
        kwargs['theme'] = None
    return _original_plotly_chart(fig, *args, **kwargs)
st.plotly_chart = custom_plotly_chart

import pandas as pd

# ─── Page Config (MUST be first Streamlit command) ───────────────────────────
st.set_page_config(
    page_title="ETA Optimization — Graph-Based Network Intelligence",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "ETA Optimization Dashboard — Powered by Graph-Based Network Intelligence"
    },
)

# ─── Imports ─────────────────────────────────────────────────────────────────
from config import COLORS, SLA_THRESHOLD
from components import inject_custom_css, render_divider
from data_loader import (
    load_featured_data, load_graph_data, load_model_comparison,
    build_network_graph, apply_filters,
)
from views import overview, network_graph, bottleneck_hubs
from views import corridor_analysis, model_performance, ftl_carting
from views import operational_insights


def main():
    """Main dashboard application entry point."""

    # ─── Inject Custom CSS ───────────────────────────────────────────────────
    inject_custom_css()

    # ─── Load Data ───────────────────────────────────────────────────────────
    with st.spinner("Loading logistics data..."):
        featured_df = load_featured_data()
        graph_df = load_graph_data()
        model_df = load_model_comparison()
        G, betweenness, degree_cent = build_network_graph(graph_df)

    # ─── Sidebar ─────────────────────────────────────────────────────────────
    with st.sidebar:
        # Logo and title
        st.markdown("""
        <div style="padding:20px 8px 12px 8px;">
            <div style="font-size:22px; font-weight:900; color:#FFFFFF; letter-spacing:-0.5px; line-height:1.1;">
                <span style="color:#D0021B;">DELHIVERY</span>
            </div>
            <div style="font-size:13px; font-weight:700; color:#F9FAFB; margin-top:6px; letter-spacing:-0.2px;">
                ETA Optimization
            </div>
            <div style="font-size:10px; color:#9CA3AF; letter-spacing:0.5px; text-transform:uppercase; margin-top:2px;">
                Graph-Based Network Intelligence
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # Navigation
        st.markdown(
            '<div style="font-size:10px; color:#6B7280; letter-spacing:1.5px; '
            'text-transform:uppercase; margin-bottom:8px; font-weight:700;">Navigation</div>',
            unsafe_allow_html=True
        )

        page = st.radio(
            "Navigate",
            options=[
                "Executive Overview",
                "Network Graph",
                "Bottleneck Hubs",
                "Corridor Analysis",
                "ML Model Performance",
                "FTL vs Carting",
                "Operational Insights",
            ],
            label_visibility="collapsed",
        )

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # ─── Global Filters ─────────────────────────────────────────────────
        st.markdown(
            '<div style="font-size:10px; color:#6B7280; letter-spacing:1.5px; '
            'text-transform:uppercase; margin-bottom:8px; font-weight:700;">Filters</div>',
            unsafe_allow_html=True
        )

        # Source hub filter
        sources = ['All'] + sorted(featured_df['source_center'].unique().tolist())
        source_hub = st.selectbox("Source Hub", sources, index=0)

        # Destination hub filter
        destinations = ['All'] + sorted(featured_df['destination_center'].unique().tolist())
        dest_hub = st.selectbox("Destination Hub", destinations, index=0)

        # Route type filter
        route_types = ['All']
        if 'route_type' in featured_df.columns:
            route_types += sorted(featured_df['route_type'].unique().tolist())
        route_type = st.selectbox("Route Type", route_types, index=0)

        # Delay threshold
        delay_threshold = st.slider(
            "Min Delay Ratio",
            min_value=0.0,
            max_value=float(featured_df['delay_ratio'].quantile(0.99)),
            value=0.0,
            step=0.1,
        )

        # Trip hour range
        if 'trip_hour' in featured_df.columns:
            trip_hour = st.slider(
                "Trip Hour Range",
                min_value=0, max_value=23,
                value=(0, 23),
            )
        else:
            trip_hour = None

        # Risk score
        risk_score = st.slider(
            "Min Risk Score",
            min_value=0.0,
            max_value=10.0,
            value=0.0,
            step=0.5,
        )

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # ─── Data Summary ───────────────────────────────────────────────────
        st.markdown(
            '<div style="font-size:10px; color:#6B7280; letter-spacing:1.5px; '
            'text-transform:uppercase; margin-bottom:8px; font-weight:700;">Data Summary</div>',
            unsafe_allow_html=True
        )

        filters = {
            'source_hub': source_hub,
            'dest_hub': dest_hub,
            'route_type': route_type,
            'delay_threshold': delay_threshold,
            'trip_hour': trip_hour,
            'risk_score': risk_score,
        }

        filtered_df = apply_filters(featured_df, filters)

        st.markdown(
            f'<div style="background:#2C2C2E; border-radius:6px; padding:12px; '
            f'font-size:13px; color:#9CA3AF;">'
            f'<div style="margin-bottom:5px;">📦 <strong style="color:#F9FAFB">{len(filtered_df):,}</strong> '
            f'<span style="color:#6B7280;">/ {len(featured_df):,} trips</span></div>'
            f'<div style="margin-bottom:5px;">🔗 <strong style="color:#F9FAFB">{len(graph_df):,}</strong> <span style="color:#6B7280;">corridors</span></div>'
            f'<div style="margin-bottom:5px;">🏢 <strong style="color:#F9FAFB">{G.number_of_nodes()}</strong> <span style="color:#6B7280;">hubs</span></div>'
            f'<div>⚠️ <strong style="color:#FCA5A5;">'
            f'{filtered_df["sla_breach"].sum():,}</strong> <span style="color:#6B7280;">SLA breaches</span></div>'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # Footer
        st.markdown(
            '<div style="text-align:left; font-size:10px; color:#6B7280; padding:8px 0; border-top:1px solid #3A3A3C; margin-top:8px;">'
            'Graph-Based Network Intelligence<br>'
            '© 2024 ETA Optimization Project'
            '</div>',
            unsafe_allow_html=True
        )

    # ─── Page Routing ────────────────────────────────────────────────────────
    if "Overview" in page:
        overview.render(filtered_df, graph_df, model_df)

    elif "Network Graph" in page:
        network_graph.render(graph_df, G, betweenness, degree_cent)

    elif "Bottleneck" in page:
        bottleneck_hubs.render(filtered_df, G, betweenness, degree_cent)

    elif "Corridor" in page:
        corridor_analysis.render(filtered_df, graph_df)

    elif "ML Model" in page:
        model_performance.render(filtered_df, model_df)

    elif "FTL" in page:
        ftl_carting.render(filtered_df, graph_df)

    elif "Operational" in page:
        operational_insights.render(filtered_df, graph_df, G, betweenness)


if __name__ == "__main__":
    main()
