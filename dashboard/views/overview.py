"""
Page 1: Executive Overview
KPI cards, summary stats, delay distribution, hourly trends.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from config import COLORS, PLOTLY_LAYOUT, CHART_COLORS, SLA_THRESHOLD
from components import (
    render_kpi_card, render_section_header, render_insight,
    render_divider, render_page_header,
)


def render(featured_df: pd.DataFrame, graph_df: pd.DataFrame, model_df: pd.DataFrame):
    """Render the Executive Overview page."""

    render_page_header(
        "Executive Overview",
        "Real-time logistics intelligence — KPIs, trends, and operational health at a glance"
    )

    # ─── KPI Row ─────────────────────────────────────────────────────────────
    total_trips = len(featured_df)
    total_corridors = graph_df['source_center'].nunique() * graph_df['destination_center'].nunique()
    unique_corridors = len(graph_df)
    avg_delay = featured_df['delay_ratio'].mean()
    avg_eta = featured_df['actual_time'].mean()
    sla_breaches = (featured_df['delay_ratio'] > SLA_THRESHOLD).sum()
    sla_rate = sla_breaches / total_trips * 100 if total_trips > 0 else 0
    unique_hubs = len(set(graph_df['source_center'].tolist() + graph_df['destination_center'].tolist()))

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        render_kpi_card("📦", f"{total_trips:,}", "Total Trips", COLORS['primary'])
    with c2:
        render_kpi_card("🔗", f"{unique_corridors:,}", "Active Corridors", COLORS['accent'])
    with c3:
        render_kpi_card("🏢", f"{unique_hubs:,}", "Network Hubs", COLORS['info'])
    with c4:
        render_kpi_card("⏱️", f"{avg_delay:.2f}x", "Avg Delay Ratio", COLORS['warning'],
                        delta=f"{sla_rate:.1f}% SLA breach", delta_positive=False)
    with c5:
        render_kpi_card("🕐", f"{avg_eta:.0f} min", "Avg ETA", COLORS['secondary'])
    with c6:
        render_kpi_card("⚠️", f"{sla_breaches:,}", "SLA Breaches", COLORS['danger'],
                        delta=f"{sla_rate:.1f}% of trips", delta_positive=False)

    render_divider()

    # ─── Charts Row 1 ────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        render_section_header("📊", "Delay Ratio Distribution",
                              "Distribution of delay ratios across all trips")
        fig = px.histogram(
            featured_df, x='delay_ratio',
            nbins=60,
            color_discrete_sequence=[COLORS['primary']],
            opacity=0.85,
        )
        fig.add_vline(x=SLA_THRESHOLD, line_dash="dash", line_color=COLORS['danger'],
                      annotation_text=f"SLA Threshold ({SLA_THRESHOLD}x)",
                      annotation_font_color=COLORS['danger'])
        fig.update_layout(
            **PLOTLY_LAYOUT,
            xaxis_title="Delay Ratio",
            yaxis_title="Trip Count",
            showlegend=False,
            height=380,
        )
        fig.update_traces(
            marker_line_width=0,
            hovertemplate="Delay Ratio: %{x:.2f}<br>Count: %{y:,}<extra></extra>"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        render_section_header("🕐", "Hourly Trip Volume & Delay",
                              "Trip distribution and average delay by hour of day")
        if 'trip_hour' in featured_df.columns:
            hourly = featured_df.groupby('trip_hour').agg(
                trip_count=('delay_ratio', 'count'),
                avg_delay=('delay_ratio', 'mean')
            ).reset_index()

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=hourly['trip_hour'], y=hourly['trip_count'],
                name='Trips',
                marker_color=COLORS['primary'],
                opacity=0.7,
                yaxis='y',
                hovertemplate="Hour: %{x}<br>Trips: %{y:,}<extra></extra>"
            ))
            fig.add_trace(go.Scatter(
                x=hourly['trip_hour'], y=hourly['avg_delay'],
                name='Avg Delay Ratio',
                line=dict(color=COLORS['secondary'], width=3),
                yaxis='y2',
                hovertemplate="Hour: %{x}<br>Avg Delay: %{y:.2f}x<extra></extra>"
            ))
            fig.update_layout(
                **PLOTLY_LAYOUT,
                height=380,
                xaxis_title="Hour of Day",
                yaxis=dict(title="Trip Count", gridcolor="rgba(148,163,184,0.1)"),
                yaxis2=dict(
                    title="Avg Delay Ratio", overlaying='y', side='right',
                    gridcolor="rgba(148,163,184,0.05)",
                ),
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1,
                    font=dict(size=11),
                ),
                barmode='overlay',
            )
            st.plotly_chart(fig, use_container_width=True)

    # ─── Charts Row 2 ────────────────────────────────────────────────────────
    col3, col4 = st.columns(2)

    with col3:
        render_section_header("🚛", "Route Type Performance",
                              "Comparison of delay ratios by transport mode")
        if 'route_type' in featured_df.columns:
            route_stats = featured_df.groupby('route_type').agg(
                avg_delay=('delay_ratio', 'mean'),
                trip_count=('delay_ratio', 'count'),
                sla_breach_pct=('sla_breach', 'mean'),
            ).reset_index()
            route_stats['sla_breach_pct'] *= 100

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=route_stats['route_type'],
                y=route_stats['avg_delay'],
                name='Avg Delay',
                marker_color=COLORS['primary'],
                text=route_stats['avg_delay'].round(2),
                textposition='outside',
                textfont=dict(color=COLORS['text_primary'], size=12),
                hovertemplate="%{x}<br>Avg Delay: %{y:.2f}x<br>Trips: %{customdata:,}<extra></extra>",
                customdata=route_stats['trip_count'],
            ))
            fig.add_trace(go.Bar(
                x=route_stats['route_type'],
                y=route_stats['sla_breach_pct'],
                name='SLA Breach %',
                marker_color=COLORS['danger'],
                opacity=0.7,
                text=route_stats['sla_breach_pct'].round(1).astype(str) + '%',
                textposition='outside',
                textfont=dict(color=COLORS['text_primary'], size=12),
                hovertemplate="%{x}<br>SLA Breach: %{y:.1f}%<extra></extra>",
            ))
            fig.update_layout(
                **PLOTLY_LAYOUT,
                height=380,
                barmode='group',
                xaxis_title="Route Type",
                yaxis_title="Value",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        render_section_header("📅", "Monthly Delay Trend",
                              "How average delay ratio evolves over months")
        if 'trip_month' in featured_df.columns:
            monthly = featured_df.groupby('trip_month').agg(
                avg_delay=('delay_ratio', 'mean'),
                trips=('delay_ratio', 'count'),
            ).reset_index()

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=monthly['trip_month'], y=monthly['avg_delay'],
                mode='lines+markers',
                line=dict(color=COLORS['accent'], width=3),
                marker=dict(size=10, color=COLORS['accent'],
                            line=dict(color=COLORS['bg_dark'], width=2)),
                fill='tozeroy',
                fillcolor='rgba(20,184,166,0.1)',
                hovertemplate="Month %{x}<br>Avg Delay: %{y:.2f}x<br>Trips: %{customdata:,}<extra></extra>",
                customdata=monthly['trips'],
            ))
            fig.update_layout(
                **PLOTLY_LAYOUT,
                height=380,
                xaxis_title="Month",
                yaxis_title="Avg Delay Ratio",
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

    render_divider()

    # ─── Executive Summary ───────────────────────────────────────────────────
    render_section_header("📋", "Executive Summary")

    top_delay_corridors = graph_df.nlargest(3, 'delay_ratio')
    top_volume_corridors = graph_df.nlargest(3, 'trip_count')

    col_a, col_b = st.columns(2)
    with col_a:
        render_insight(
            f"<strong>Network Scale:</strong> {unique_hubs} hubs connected by {unique_corridors} corridors, "
            f"processing <strong>{total_trips:,}</strong> trips. "
            f"Average ETA is <strong>{avg_eta:.0f} minutes</strong> with a mean delay ratio of <strong>{avg_delay:.2f}x</strong>."
        )
        render_insight(
            f"<strong>SLA Performance:</strong> <strong>{sla_breaches:,}</strong> trips "
            f"(<strong>{sla_rate:.1f}%</strong>) exceeded the {SLA_THRESHOLD}x delay threshold. "
            f"Targeted corridor optimization could reduce breaches by an estimated 20-35%.",
            box_type="warning"
        )

    with col_b:
        top_names = ", ".join(top_delay_corridors['source_center'].values[:3])
        render_insight(
            f"<strong>Highest Delay Corridors</strong> originate from: <strong>{top_names}</strong>. "
            f"These corridors have delay ratios exceeding <strong>"
            f"{top_delay_corridors['delay_ratio'].values[0]:.1f}x</strong>.",
            box_type="danger"
        )
        vol_names = ", ".join(top_volume_corridors['source_center'].values[:3])
        render_insight(
            f"<strong>Busiest Corridors</strong> originate from: <strong>{vol_names}</strong> "
            f"with up to <strong>{top_volume_corridors['trip_count'].values[0]:,}</strong> trips. "
            f"Capacity planning should prioritize these routes.",
            box_type="success"
        )
