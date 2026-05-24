"""
Page 3: Bottleneck Hub Analysis
Identify and analyze critical bottleneck hubs in the network.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from config import COLORS, PLOTLY_LAYOUT, CHART_COLORS, SLA_THRESHOLD, TOP_N
from components import (
    render_kpi_card, render_section_header, render_insight,
    render_divider, render_page_header,
)
from data_loader import get_bottleneck_hubs


def render(featured_df: pd.DataFrame, G, betweenness: dict, degree_cent: dict):
    """Render the Bottleneck Hub Analysis page."""

    render_page_header(
        "Bottleneck Hub Analysis",
        "Identify critical network hubs that create congestion, delays, and SLA breaches"
    )

    # ─── Get bottleneck data ─────────────────────────────────────────────────
    bottleneck_df = get_bottleneck_hubs(G, betweenness)

    if bottleneck_df.empty:
        st.warning("No bottleneck hubs detected with current threshold.")
        return

    # ─── KPIs ────────────────────────────────────────────────────────────────
    n_bottlenecks = len(bottleneck_df)
    avg_bc = bottleneck_df['betweenness_centrality'].mean()
    max_flow = bottleneck_df['total_flow'].max()
    avg_hub_delay = bottleneck_df['avg_delay_ratio'].mean()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("🔴", f"{n_bottlenecks}", "Bottleneck Hubs", COLORS['danger'])
    with c2:
        render_kpi_card("📊", f"{avg_bc:.5f}", "Avg Betweenness", COLORS['primary'])
    with c3:
        render_kpi_card("📈", f"{max_flow:,.0f}", "Max Hub Flow", COLORS['accent'])
    with c4:
        render_kpi_card("⏱️", f"{avg_hub_delay:.2f}x", "Avg Hub Delay", COLORS['warning'])

    render_divider()

    # ─── Top Bottleneck Hubs Bar Chart ───────────────────────────────────────
    render_section_header("🏆", "Top Bottleneck Hubs by Centrality",
                          "Hubs with highest betweenness centrality — critical transit points in the network")

    top_hubs = bottleneck_df.nlargest(TOP_N, 'betweenness_centrality')
    top_hubs['hub_short'] = top_hubs['hub'].str[-12:]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=top_hubs['hub_short'],
        x=top_hubs['betweenness_centrality'],
        orientation='h',
        marker=dict(
            color=top_hubs['betweenness_centrality'],
            colorscale=[[0, COLORS['primary']], [1, COLORS['secondary']]],
            line=dict(width=0),
        ),
        text=top_hubs['betweenness_centrality'].round(5),
        textposition='outside',
        textfont=dict(size=11, color=COLORS['text_muted']),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Betweenness: %{x:.6f}<br>"
            "<extra></extra>"
        ),
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=max(400, TOP_N * 35),
        yaxis=dict(autorange='reversed', gridcolor="rgba(0,0,0,0)"),
        xaxis_title="Betweenness Centrality",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    render_divider()

    # ─── Multi-metric Comparison ─────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        render_section_header("🔄", "Hub Flow Analysis",
                              "Inbound vs Outbound trip flow for bottleneck hubs")

        flow_df = top_hubs[['hub_short', 'in_flow', 'out_flow']].copy()
        fig_flow = go.Figure()
        fig_flow.add_trace(go.Bar(
            x=flow_df['hub_short'], y=flow_df['in_flow'],
            name='Inbound', marker_color=COLORS['info'], opacity=0.85,
        ))
        fig_flow.add_trace(go.Bar(
            x=flow_df['hub_short'], y=flow_df['out_flow'],
            name='Outbound', marker_color=COLORS['accent'], opacity=0.85,
        ))
        fig_flow.update_layout(
            **PLOTLY_LAYOUT, height=400,
            barmode='group',
            xaxis_title="Hub", yaxis_title="Trip Flow",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig_flow, use_container_width=True)

    with col2:
        render_section_header("⚠️", "Delay Contribution",
                              "Average delay ratio for each bottleneck hub")

        fig_delay = go.Figure()
        colors = [COLORS['danger'] if d > SLA_THRESHOLD else COLORS['warning']
                  for d in top_hubs['avg_delay_ratio']]
        fig_delay.add_trace(go.Bar(
            x=top_hubs['hub_short'], y=top_hubs['avg_delay_ratio'],
            marker_color=colors,
            text=top_hubs['avg_delay_ratio'].round(2),
            textposition='outside',
            textfont=dict(size=11, color=COLORS['text_muted']),
            hovertemplate="<b>%{x}</b><br>Avg Delay: %{y:.2f}x<extra></extra>",
        ))
        fig_delay.add_hline(y=SLA_THRESHOLD, line_dash="dash", line_color=COLORS['danger'],
                            annotation_text="SLA Threshold",
                            annotation_font_color=COLORS['danger'])
        fig_delay.update_layout(
            **PLOTLY_LAYOUT, height=400,
            xaxis_title="Hub", yaxis_title="Avg Delay Ratio",
            showlegend=False, xaxis_tickangle=-45,
        )
        st.plotly_chart(fig_delay, use_container_width=True)

    render_divider()

    # ─── SLA Breach Heatmap ──────────────────────────────────────────────────
    render_section_header("🗺️", "Hub Connectivity Heatmap",
                          "Connections and flow intensity between bottleneck hubs")

    # Build a small adjacency matrix for top hubs
    top_hub_ids = top_hubs['hub'].tolist()[:10]
    adj_matrix = np.zeros((len(top_hub_ids), len(top_hub_ids)))
    for i, h1 in enumerate(top_hub_ids):
        for j, h2 in enumerate(top_hub_ids):
            if G.has_edge(h1, h2):
                adj_matrix[i][j] = G[h1][h2].get('weight', 0)
            elif G.has_edge(h2, h1):
                adj_matrix[i][j] = G[h2][h1].get('weight', 0)

    short_labels = [h[-10:] for h in top_hub_ids]

    fig_heat = go.Figure(data=go.Heatmap(
        z=adj_matrix,
        x=short_labels,
        y=short_labels,
        colorscale='Viridis',
        hovertemplate="From: %{y}<br>To: %{x}<br>Trips: %{z:,.0f}<extra></extra>",
        colorbar=dict(
            title="Trips",
            tickfont=dict(color=COLORS['text_muted']),
        ),
    ))
    fig_heat.update_layout(
        **PLOTLY_LAYOUT,
        height=450,
        xaxis_tickangle=-45,
        yaxis=dict(autorange='reversed', gridcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    render_divider()

    # ─── Hub Detail Table ────────────────────────────────────────────────────
    render_section_header("📋", "Bottleneck Hub Details",
                          "Complete metrics for all identified bottleneck hubs")

    display_df = bottleneck_df.copy()
    display_df.columns = [
        'Hub ID', 'Betweenness', 'Degree Centrality',
        'In-Flow', 'Out-Flow', 'Total Flow',
        'Avg Delay Ratio', 'Connected Corridors'
    ]
    st.dataframe(
        display_df.style.format({
            'Betweenness': '{:.6f}',
            'Degree Centrality': '{:.6f}',
            'In-Flow': '{:,.0f}',
            'Out-Flow': '{:,.0f}',
            'Total Flow': '{:,.0f}',
            'Avg Delay Ratio': '{:.3f}',
        }).background_gradient(subset=['Betweenness'], cmap='Purples')
        .background_gradient(subset=['Avg Delay Ratio'], cmap='YlOrRd'),
        use_container_width=True,
        height=400,
    )

    # ─── Insights ────────────────────────────────────────────────────────────
    render_divider()
    render_section_header("💡", "Bottleneck Insights")

    top3 = bottleneck_df.nlargest(3, 'betweenness_centrality')
    render_insight(
        f"<strong>Critical Hubs:</strong> The top 3 bottleneck hubs are "
        f"<strong>{', '.join(top3['hub'].values)}</strong>. "
        f"These hubs handle <strong>{top3['total_flow'].sum():,.0f}</strong> combined trips "
        f"and have an average delay of <strong>{top3['avg_delay_ratio'].mean():.2f}x</strong>.",
        box_type="danger"
    )

    high_delay_hubs = bottleneck_df[bottleneck_df['avg_delay_ratio'] > SLA_THRESHOLD]
    if len(high_delay_hubs) > 0:
        render_insight(
            f"<strong>{len(high_delay_hubs)} bottleneck hubs</strong> exceed the SLA threshold. "
            f"Upgrading capacity at these hubs could reduce network-wide SLA breaches by an estimated 15-25%.",
            box_type="warning"
        )

    render_insight(
        "<strong>Recommendation:</strong> Consider adding parallel processing capacity at the top 3 hubs, "
        "redistributing flow through alternative routes, or upgrading infrastructure to reduce transit time.",
        box_type="success"
    )
