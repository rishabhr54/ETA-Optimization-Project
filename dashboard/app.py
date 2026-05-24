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
        <div style="text-align:center; padding:16px 0 8px 0;">
            <div style="font-size:40px; margin-bottom:4px;">🚛</div>
            <div style="font-size:18px; font-weight:800;
                 background: linear-gradient(135deg, #6366F1, #EC4899);
                 -webkit-background-clip: text;
                 -webkit-text-fill-color: transparent;">
                ETA Optimization
            </div>
            <div style="font-size:11px; color:#94A3B8; letter-spacing:1px; text-transform:uppercase;">
                Graph-Based Network Intelligence
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # Navigation
        st.markdown(
            '<div style="font-size:11px; color:#94A3B8; letter-spacing:1.5px; '
            'text-transform:uppercase; margin-bottom:8px; font-weight:600;">Navigation</div>',
            unsafe_allow_html=True
        )

        page = st.radio(
            "Navigate",
            options=[
                "📊 Executive Overview",
                "🌐 Network Graph",
                "🔴 Bottleneck Hubs",
                "🔗 Corridor Analysis",
                "🤖 ML Model Performance",
                "🚛 FTL vs Carting",
                "💡 Operational Insights",
            ],
            label_visibility="collapsed",
        )

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # ─── Global Filters ─────────────────────────────────────────────────
        st.markdown(
            '<div style="font-size:11px; color:#94A3B8; letter-spacing:1.5px; '
            'text-transform:uppercase; margin-bottom:8px; font-weight:600;">Filters</div>',
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
            '<div style="font-size:11px; color:#94A3B8; letter-spacing:1.5px; '
            'text-transform:uppercase; margin-bottom:8px; font-weight:600;">Data Summary</div>',
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
            f'<div style="background:rgba(99,102,241,0.08); border-radius:10px; padding:12px; '
            f'font-size:13px; color:{COLORS["text_muted"]};">'
            f'<div>📦 <strong style="color:{COLORS["text_primary"]}">{len(filtered_df):,}</strong> '
            f'/ {len(featured_df):,} trips</div>'
            f'<div>🔗 <strong style="color:{COLORS["text_primary"]}">{len(graph_df):,}</strong> corridors</div>'
            f'<div>🏢 <strong style="color:{COLORS["text_primary"]}">{G.number_of_nodes()}</strong> hubs</div>'
            f'<div>⚠️ <strong style="color:{COLORS["danger"]}">'
            f'{filtered_df["sla_breach"].sum():,}</strong> SLA breaches</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # Footer
        st.markdown(
            f'<div style="text-align:center; font-size:10px; color:{COLORS["text_muted"]}; padding:8px 0;">'
            f'Powered by Graph Neural Intelligence<br>'
            f'© 2024 ETA Optimization Project'
            f'</div>',
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
