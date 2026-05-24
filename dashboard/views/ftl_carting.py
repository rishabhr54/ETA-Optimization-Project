"""
Page 6: FTL vs Carting Intelligence
Transport mode analysis and operational recommendations.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from config import COLORS, PLOTLY_LAYOUT, CHART_COLORS, SLA_THRESHOLD, TOP_N
from components import (
    render_kpi_card, render_section_header, render_insight,
    render_divider, render_page_header,
)


def render(featured_df: pd.DataFrame, graph_df: pd.DataFrame):
    """Render the FTL vs Carting Intelligence page."""

    render_page_header(
        "FTL vs Carting Intelligence",
        "Data-driven transport mode analysis — optimize between Full Truck Load and Carting operations"
    )

    # ─── Mode statistics ─────────────────────────────────────────────────────
    if 'route_type' not in featured_df.columns:
        st.warning("Route type information not available in the dataset.")
        return

    mode_stats = featured_df.groupby('route_type').agg(
        trip_count=('delay_ratio', 'count'),
        avg_delay=('delay_ratio', 'mean'),
        median_delay=('delay_ratio', 'median'),
        sla_breach_rate=('sla_breach', 'mean'),
        avg_distance=('actual_distance_to_destination', 'mean'),
        avg_time=('actual_time', 'mean'),
        avg_speed=('avg_speed', lambda x: x.dropna().mean()),
    ).reset_index()
    mode_stats['sla_breach_rate'] *= 100

    # Recommended mode analysis
    has_recommended = 'recommended_mode' in featured_df.columns
    if has_recommended:
        rec_stats = featured_df.groupby('recommended_mode').agg(
            trip_count=('delay_ratio', 'count'),
            avg_delay=('delay_ratio', 'mean'),
        ).reset_index()

    # ─── KPIs ────────────────────────────────────────────────────────────────
    ftl_data = mode_stats[mode_stats['route_type'] == 'FTL']
    carting_data = mode_stats[mode_stats['route_type'] == 'Carting']

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        ftl_count = ftl_data['trip_count'].values[0] if len(ftl_data) > 0 else 0
        render_kpi_card("🚛", f"{ftl_count:,}", "FTL Trips", COLORS['primary'])
    with c2:
        cart_count = carting_data['trip_count'].values[0] if len(carting_data) > 0 else 0
        render_kpi_card("📦", f"{cart_count:,}", "Carting Trips", COLORS['accent'])
    with c3:
        ftl_delay = ftl_data['avg_delay'].values[0] if len(ftl_data) > 0 else 0
        render_kpi_card("⏱️", f"{ftl_delay:.2f}x", "FTL Avg Delay", COLORS['info'])
    with c4:
        cart_delay = carting_data['avg_delay'].values[0] if len(carting_data) > 0 else 0
        render_kpi_card("⏱️", f"{cart_delay:.2f}x", "Carting Avg Delay",
                        COLORS['warning'] if cart_delay > ftl_delay else COLORS['success'])
    with c5:
        cart_sla = carting_data['sla_breach_rate'].values[0] if len(carting_data) > 0 else 0
        render_kpi_card("⚠️", f"{cart_sla:.1f}%", "Carting SLA Breach",
                        COLORS['danger'] if cart_sla > 15 else COLORS['warning'])

    render_divider()

    # ─── Performance Comparison ──────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        render_section_header("📊", "Delay Distribution by Mode",
                              "Compare delay patterns between FTL and Carting")

        fig = go.Figure()
        for i, mode in enumerate(featured_df['route_type'].unique()):
            mode_data = featured_df[featured_df['route_type'] == mode]['delay_ratio']
            fig.add_trace(go.Violin(
                y=mode_data.clip(upper=mode_data.quantile(0.95)),
                name=mode,
                box_visible=True,
                meanline_visible=True,
                fillcolor=CHART_COLORS[i % len(CHART_COLORS)],
                opacity=0.7,
                line_color=CHART_COLORS[i % len(CHART_COLORS)],
            ))
        fig.add_hline(y=SLA_THRESHOLD, line_dash="dash", line_color=COLORS['danger'],
                      annotation_text="SLA Threshold")
        fig.update_layout(
            **PLOTLY_LAYOUT, height=420,
            yaxis_title="Delay Ratio",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        render_section_header("🎯", "SLA Breach Rate by Mode",
                              "Percentage of trips exceeding SLA threshold")

        fig_sla = go.Figure()
        fig_sla.add_trace(go.Bar(
            x=mode_stats['route_type'],
            y=mode_stats['sla_breach_rate'],
            marker=dict(
                color=[COLORS['danger'] if r > 15 else COLORS['warning']
                       for r in mode_stats['sla_breach_rate']],
            ),
            text=mode_stats['sla_breach_rate'].round(1).astype(str) + '%',
            textposition='outside',
            textfont=dict(size=14, color=COLORS['text_primary'], weight='bold'),
            hovertemplate="%{x}<br>SLA Breach: %{y:.1f}%<br>Trips: %{customdata:,}<extra></extra>",
            customdata=mode_stats['trip_count'],
        ))
        fig_sla.update_layout(
            **PLOTLY_LAYOUT, height=420,
            yaxis_title="SLA Breach Rate (%)",
            showlegend=False,
        )
        st.plotly_chart(fig_sla, use_container_width=True)

    render_divider()

    # ─── Route-Type by Hour ──────────────────────────────────────────────────
    render_section_header("🕐", "Mode Performance by Hour",
                          "How FTL and Carting performance varies throughout the day")

    if 'trip_hour' in featured_df.columns:
        hourly_mode = featured_df.groupby(['trip_hour', 'route_type']).agg(
            avg_delay=('delay_ratio', 'mean'),
            trip_count=('delay_ratio', 'count'),
        ).reset_index()

        fig_hourly = go.Figure()
        for i, mode in enumerate(hourly_mode['route_type'].unique()):
            mode_data = hourly_mode[hourly_mode['route_type'] == mode]
            fig_hourly.add_trace(go.Scatter(
                x=mode_data['trip_hour'],
                y=mode_data['avg_delay'],
                mode='lines+markers',
                name=mode,
                line=dict(color=CHART_COLORS[i], width=3),
                marker=dict(size=8),
                hovertemplate=f"{mode}<br>Hour: %{{x}}<br>Avg Delay: %{{y:.2f}}x<br>Trips: %{{customdata:,}}<extra></extra>",
                customdata=mode_data['trip_count'],
            ))
        fig_hourly.add_hline(y=SLA_THRESHOLD, line_dash="dash", line_color=COLORS['danger'],
                             annotation_text="SLA Threshold",
                             annotation_font_color=COLORS['danger'])
        fig_hourly.update_layout(
            **PLOTLY_LAYOUT, height=400,
            xaxis_title="Hour of Day",
            yaxis_title="Avg Delay Ratio",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_hourly, use_container_width=True)

    render_divider()

    # ─── High-Risk Carting Corridors ─────────────────────────────────────────
    render_section_header("🔴", "High-Risk Carting Corridors",
                          "Carting corridors with excessive delays — candidates for FTL conversion")

    carting_trips = featured_df[featured_df['route_type'] == 'Carting'].copy()
    if len(carting_trips) > 0:
        carting_corridor = carting_trips.groupby(['source_center', 'destination_center']).agg(
            avg_delay=('delay_ratio', 'mean'),
            trip_count=('delay_ratio', 'count'),
            sla_breach_pct=('sla_breach', 'mean'),
            avg_distance=('actual_distance_to_destination', 'mean'),
        ).reset_index()
        carting_corridor['sla_breach_pct'] *= 100
        carting_corridor['corridor'] = (
            carting_corridor['source_center'].str[-8:] + ' → ' +
            carting_corridor['destination_center'].str[-8:]
        )

        high_risk_carting = carting_corridor[
            carting_corridor['avg_delay'] > SLA_THRESHOLD
        ].nlargest(TOP_N, 'avg_delay')

        if len(high_risk_carting) > 0:
            fig_risk = go.Figure()
            fig_risk.add_trace(go.Bar(
                y=high_risk_carting['corridor'],
                x=high_risk_carting['avg_delay'],
                orientation='h',
                marker=dict(
                    color=high_risk_carting['avg_delay'],
                    colorscale=[[0, '#F59E0B'], [1, '#EF4444']],
                ),
                text=high_risk_carting['avg_delay'].round(2).astype(str) + 'x',
                textposition='outside',
                textfont=dict(size=11, color=COLORS['text_muted']),
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Avg Delay: %{x:.2f}x<br>"
                    "Trips: %{customdata[0]:,}<br>"
                    "SLA Breach: %{customdata[1]:.1f}%<br>"
                    "Avg Distance: %{customdata[2]:.1f} km"
                    "<extra></extra>"
                ),
                customdata=np.column_stack([
                    high_risk_carting['trip_count'],
                    high_risk_carting['sla_breach_pct'],
                    high_risk_carting['avg_distance'],
                ]),
            ))
            fig_risk.update_layout(
                **PLOTLY_LAYOUT,
                height=max(350, len(high_risk_carting) * 35),
                yaxis=dict(autorange='reversed', gridcolor="rgba(0,0,0,0)"),
                xaxis_title="Average Delay Ratio",
                showlegend=False,
            )
            st.plotly_chart(fig_risk, use_container_width=True)
        else:
            st.info("No carting corridors exceed the SLA threshold.")

    render_divider()

    # ─── Recommended Mode Analysis ───────────────────────────────────────────
    if has_recommended:
        render_section_header("🧠", "AI-Recommended Transport Mode",
                              "Data-driven mode recommendations based on corridor characteristics")

        col_a, col_b = st.columns(2)
        with col_a:
            fig_rec = px.pie(
                rec_stats, values='trip_count', names='recommended_mode',
                color_discrete_sequence=[COLORS['primary'], COLORS['accent']],
                hole=0.55,
            )
            fig_rec.update_traces(
                textinfo='percent+label',
                textfont_size=14,
                hovertemplate="%{label}<br>Trips: %{value:,}<br>Share: %{percent}<extra></extra>",
            )
            fig_rec.update_layout(
                **PLOTLY_LAYOUT, height=350,
                showlegend=False,
                annotations=[dict(
                    text="Mode<br>Split",
                    x=0.5, y=0.5, font_size=16, showarrow=False,
                    font_color=COLORS['text_muted'],
                )],
            )
            st.plotly_chart(fig_rec, use_container_width=True)

        with col_b:
            # Mode mismatch analysis
            if 'route_type' in featured_df.columns:
                mismatch = featured_df[
                    featured_df['route_type'] != featured_df['recommended_mode']
                ]
                mismatch_pct = len(mismatch) / len(featured_df) * 100

                render_insight(
                    f"<strong>Mode Mismatch Detected:</strong> <strong>{mismatch_pct:.1f}%</strong> of trips "
                    f"({len(mismatch):,} trips) are using a different mode than recommended. "
                    f"Optimizing mode assignment could reduce delays and operational costs.",
                    box_type="warning"
                )

                mismatch_impact = mismatch.groupby(['route_type', 'recommended_mode']).agg(
                    count=('delay_ratio', 'count'),
                    avg_delay=('delay_ratio', 'mean'),
                ).reset_index()

                if len(mismatch_impact) > 0:
                    render_insight(
                        "<strong>Mismatch Breakdown:</strong><br>" +
                        "<br>".join([
                            f"• {row['route_type']} → should be {row['recommended_mode']}: "
                            f"<strong>{row['count']:,}</strong> trips, avg delay <strong>{row['avg_delay']:.2f}x</strong>"
                            for _, row in mismatch_impact.iterrows()
                        ]),
                        box_type="danger"
                    )

    render_divider()

    # ─── Decision Recommendations ────────────────────────────────────────────
    render_section_header("💡", "Operational Recommendations")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if len(carting_data) > 0 and len(ftl_data) > 0:
            delay_diff = cart_delay - ftl_delay
            render_insight(
                f"<strong>Mode Efficiency Gap:</strong> Carting corridors experience "
                f"<strong>{delay_diff:.2f}x higher average delay</strong> than FTL routes. "
                f"Converting top {TOP_N} high-risk carting corridors to FTL could reduce "
                f"SLA breaches by an estimated 15-25%.",
                box_type="insight"
            )

        render_insight(
            "<strong>FTL Conversion Criteria:</strong><br>"
            "• Average distance > 200 km<br>"
            "• Consistent delay ratio > 1.5x<br>"
            "• Trip volume > 10 trips/corridor<br>"
            "• SLA breach rate > 20%",
            box_type="success"
        )

    with col_r2:
        render_insight(
            "<strong>Carting Optimization:</strong> For corridors that must remain Carting, consider:<br>"
            "• Time-window optimization to avoid peak congestion<br>"
            "• Multi-stop route consolidation<br>"
            "• Hub-level batching improvements<br>"
            "• Dynamic re-routing during delays",
            box_type="insight"
        )

        render_insight(
            "<strong>Immediate Actions:</strong><br>"
            "1. Convert top 10 high-risk carting corridors to FTL<br>"
            "2. Implement time-of-day mode switching for medium-risk corridors<br>"
            "3. Add surge capacity at bottleneck hubs during peak hours",
            box_type="warning"
        )
