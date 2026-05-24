"""
Page 4: Corridor Analysis
Detailed analysis of logistics corridors — delays, risk scores, congestion.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from config import COLORS, PLOTLY_LAYOUT, CHART_COLORS, SLA_THRESHOLD, TOP_N, HIGH_RISK_SCORE
from components import (
    render_kpi_card, render_section_header, render_insight,
    render_divider, render_page_header,
)
from data_loader import get_corridor_stats


def render(featured_df: pd.DataFrame, graph_df: pd.DataFrame):
    """Render the Corridor Analysis page."""

    render_page_header(
        "Corridor Analysis",
        "Deep-dive into corridor performance — identify delays, congestion, and high-risk routes"
    )

    corridor_df = get_corridor_stats(graph_df)

    # ─── KPIs ────────────────────────────────────────────────────────────────
    total_corridors = len(corridor_df)
    avg_delay = corridor_df['delay_ratio'].mean()
    high_risk = (corridor_df['risk_score'] > HIGH_RISK_SCORE).sum()
    sla_breached = (corridor_df['delay_ratio'] > SLA_THRESHOLD).sum()
    avg_trips = corridor_df['trip_count'].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_kpi_card("🔗", f"{total_corridors}", "Total Corridors", COLORS['primary'])
    with c2:
        render_kpi_card("⏱️", f"{avg_delay:.2f}x", "Avg Delay", COLORS['warning'])
    with c3:
        render_kpi_card("🔥", f"{high_risk}", "High-Risk", COLORS['danger'])
    with c4:
        render_kpi_card("⚠️", f"{sla_breached}", "SLA Breach", COLORS['secondary'])
    with c5:
        render_kpi_card("📦", f"{avg_trips:.0f}", "Avg Trips/Corridor", COLORS['accent'])

    render_divider()

    # ─── Corridor Search ─────────────────────────────────────────────────────
    render_section_header("🔍", "Corridor Explorer",
                          "Search and filter corridors by source, destination, or delay threshold")

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        search_term = st.text_input("🔎 Search corridor",
                                    placeholder="Type hub name...",
                                    help="Search by source or destination hub ID")
    with col_f2:
        delay_filter = st.slider("Min Delay Ratio", 0.0, float(corridor_df['delay_ratio'].max()),
                                 value=0.0, step=0.1)
    with col_f3:
        trip_filter = st.slider("Min Trip Count", 1, int(corridor_df['trip_count'].max()),
                                value=1)

    # Apply filters
    filtered = corridor_df.copy()
    if search_term:
        filtered = filtered[
            filtered['corridor'].str.contains(search_term, case=False, na=False)
        ]
    filtered = filtered[
        (filtered['delay_ratio'] >= delay_filter) &
        (filtered['trip_count'] >= trip_filter)
    ]

    st.caption(f"Showing {len(filtered):,} of {total_corridors:,} corridors")

    render_divider()

    # ─── Most Delayed Corridors ──────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        render_section_header("🔴", "Most Delayed Corridors",
                              f"Top {TOP_N} corridors by delay ratio")

        top_delayed = filtered.nlargest(TOP_N, 'delay_ratio')
        top_delayed['corridor_short'] = (
            top_delayed['source_center'].str[-8:] + ' → ' +
            top_delayed['destination_center'].str[-8:]
        )

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=top_delayed['corridor_short'],
            x=top_delayed['delay_ratio'],
            orientation='h',
            marker=dict(
                color=top_delayed['delay_ratio'],
                colorscale=[[0, '#F59E0B'], [0.5, '#F97316'], [1, '#EF4444']],
            ),
            text=top_delayed['delay_ratio'].round(2).astype(str) + 'x',
            textposition='outside',
            textfont=dict(size=11, color=COLORS['text_muted']),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Delay: %{x:.2f}x<br>"
                "Trips: %{customdata}<extra></extra>"
            ),
            customdata=top_delayed['trip_count'],
        ))
        fig.add_vline(x=SLA_THRESHOLD, line_dash="dash", line_color=COLORS['danger'],
                      annotation_text="SLA", annotation_font_color=COLORS['danger'])
        fig.update_layout(
            **PLOTLY_LAYOUT,
            height=max(400, TOP_N * 35),
            yaxis=dict(autorange='reversed', gridcolor="rgba(0,0,0,0)"),
            xaxis_title="Delay Ratio",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        render_section_header("🔥", "Highest Risk Corridors",
                              f"Top {TOP_N} corridors by composite risk score")

        top_risky = filtered.nlargest(TOP_N, 'risk_score')
        top_risky['corridor_short'] = (
            top_risky['source_center'].str[-8:] + ' → ' +
            top_risky['destination_center'].str[-8:]
        )

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=top_risky['corridor_short'],
            x=top_risky['risk_score'],
            orientation='h',
            marker=dict(
                color=top_risky['risk_score'],
                colorscale=[[0, '#6366F1'], [0.5, '#EC4899'], [1, '#EF4444']],
            ),
            text=top_risky['risk_score'].round(2),
            textposition='outside',
            textfont=dict(size=11, color=COLORS['text_muted']),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Risk Score: %{x:.2f}<br>"
                "Trips: %{customdata}<extra></extra>"
            ),
            customdata=top_risky['trip_count'],
        ))
        fig.update_layout(
            **PLOTLY_LAYOUT,
            height=max(400, TOP_N * 35),
            yaxis=dict(autorange='reversed', gridcolor="rgba(0,0,0,0)"),
            xaxis_title="Risk Score",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    render_divider()

    # ─── Corridor Scatter ────────────────────────────────────────────────────
    render_section_header("📊", "Corridor Performance Scatter",
                          "Trip volume vs. delay ratio — bubble size = risk score")

    fig_scatter = px.scatter(
        filtered,
        x='trip_count', y='delay_ratio',
        size='risk_score',
        color='delay_ratio',
        color_continuous_scale=[[0, '#22C55E'], [0.3, '#F59E0B'], [0.7, '#F97316'], [1, '#EF4444']],
        hover_data={
            'source_center': True,
            'destination_center': True,
            'trip_count': ':,',
            'delay_ratio': ':.2f',
            'risk_score': ':.2f',
        },
        labels={
            'trip_count': 'Trip Count',
            'delay_ratio': 'Delay Ratio',
            'risk_score': 'Risk Score',
        },
    )
    fig_scatter.add_hline(y=SLA_THRESHOLD, line_dash="dash", line_color=COLORS['danger'],
                          annotation_text="SLA Threshold",
                          annotation_font_color=COLORS['danger'])
    fig_scatter.update_layout(**PLOTLY_LAYOUT, height=500)
    fig_scatter.update_traces(
        marker=dict(line=dict(width=0.5, color='rgba(255,255,255,0.2)')),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    render_divider()

    # ─── Congestion Heatmap ──────────────────────────────────────────────────
    render_section_header("🗺️", "Corridor Congestion Matrix",
                          "Delay patterns between top source and destination hubs")

    # Get top sources and destinations by volume
    top_src = filtered.groupby('source_center')['trip_count'].sum().nlargest(12).index
    top_dst = filtered.groupby('destination_center')['trip_count'].sum().nlargest(12).index

    matrix_data = filtered[
        filtered['source_center'].isin(top_src) &
        filtered['destination_center'].isin(top_dst)
    ].pivot_table(
        index='source_center', columns='destination_center',
        values='delay_ratio', aggfunc='mean'
    ).fillna(0)

    if not matrix_data.empty:
        fig_matrix = go.Figure(data=go.Heatmap(
            z=matrix_data.values,
            x=[c[-10:] for c in matrix_data.columns],
            y=[r[-10:] for r in matrix_data.index],
            colorscale=[[0, '#22C55E'], [0.3, '#F59E0B'], [0.6, '#F97316'], [1, '#EF4444']],
            hovertemplate="From: %{y}<br>To: %{x}<br>Delay: %{z:.2f}x<extra></extra>",
            colorbar=dict(
                title="Delay Ratio",
                tickfont=dict(color=COLORS['text_muted']),
            ),
        ))
        fig_matrix.update_layout(
            **PLOTLY_LAYOUT, height=500,
            xaxis_tickangle=-45,
            yaxis=dict(autorange='reversed', gridcolor="rgba(0,0,0,0)"),
            xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_matrix, use_container_width=True)

    render_divider()

    # ─── Trip Volume Distribution ────────────────────────────────────────────
    render_section_header("📦", "Trip Volume Distribution",
                          "How trip volumes are distributed across corridors")

    fig_vol = px.histogram(
        corridor_df, x='trip_count', nbins=50,
        color_discrete_sequence=[COLORS['accent']],
        opacity=0.85,
    )
    fig_vol.update_layout(
        **PLOTLY_LAYOUT, height=350,
        xaxis_title="Trips per Corridor",
        yaxis_title="Number of Corridors",
        showlegend=False,
    )
    st.plotly_chart(fig_vol, use_container_width=True)

    # ─── Insights ────────────────────────────────────────────────────────────
    render_divider()
    render_section_header("💡", "Corridor Insights")

    pct_high_risk = high_risk / total_corridors * 100 if total_corridors > 0 else 0
    render_insight(
        f"<strong>{high_risk} corridors ({pct_high_risk:.1f}%)</strong> have risk scores above {HIGH_RISK_SCORE}. "
        f"These corridors should be prioritized for route optimization and capacity upgrades.",
        box_type="danger"
    )

    pct_sla = sla_breached / total_corridors * 100 if total_corridors > 0 else 0
    render_insight(
        f"<strong>{sla_breached} corridors ({pct_sla:.1f}%)</strong> consistently exceed the SLA threshold of {SLA_THRESHOLD}x. "
        f"Switching to FTL mode on these corridors could reduce delays by 20-40%.",
        box_type="warning"
    )
