"""
Page 2: Interactive Network Graph
Visualize the hub-and-spoke logistics network with Plotly.
"""

import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import numpy as np
import pandas as pd
from config import COLORS, PLOTLY_LAYOUT, DELAY_COLORSCALE, SLA_THRESHOLD
from components import (
    render_kpi_card, render_section_header, render_insight,
    render_divider, render_page_header,
)


def render(graph_df: pd.DataFrame, G: nx.DiGraph, betweenness: dict, degree_cent: dict):
    """Render the Network Graph visualization page."""

    render_page_header(
        "Network Intelligence",
        "Interactive logistics network — explore hub connectivity, corridor delays, and bottleneck patterns"
    )

    # ─── Network KPIs ────────────────────────────────────────────────────────
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    density = nx.density(G)
    avg_clustering = nx.average_clustering(G.to_undirected()) if n_nodes > 0 else 0
    top_hub = max(betweenness, key=betweenness.get) if betweenness else "N/A"
    top_bc = betweenness.get(top_hub, 0)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_kpi_card("🏢", f"{n_nodes}", "Network Hubs", COLORS['primary'])
    with c2:
        render_kpi_card("🔗", f"{n_edges}", "Corridors", COLORS['accent'])
    with c3:
        render_kpi_card("📐", f"{density:.4f}", "Network Density", COLORS['info'])
    with c4:
        render_kpi_card("🔄", f"{avg_clustering:.3f}", "Avg Clustering", COLORS['secondary'])
    with c5:
        render_kpi_card("⭐", top_hub[-8:], "Top Hub (BC)", COLORS['warning'])

    render_divider()

    # ─── Controls ────────────────────────────────────────────────────────────
    render_section_header("🌐", "Interactive Network Graph",
                          "Hub-and-spoke logistics network — node size = centrality, edge color = delay severity")

    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
    with col_ctrl1:
        min_trips = st.slider("Min Trip Count (edge filter)", 1, int(graph_df['trip_count'].max()),
                              value=max(1, int(graph_df['trip_count'].quantile(0.5))),
                              help="Filter corridors with fewer trips for clarity")
    with col_ctrl2:
        layout_algo = st.selectbox("Layout Algorithm",
                                   ["Spring", "Kamada-Kawai", "Circular", "Shell"],
                                   help="Choose network layout algorithm")
    with col_ctrl3:
        node_scale = st.slider("Node Size Scale", 5, 50, 20,
                               help="Adjust node size multiplier")

    # ─── Build filtered subgraph ─────────────────────────────────────────────
    filtered_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('weight', 0) >= min_trips]
    subG = G.edge_subgraph(filtered_edges).copy() if filtered_edges else G.copy()

    # ─── Compute layout ─────────────────────────────────────────────────────
    if layout_algo == "Spring":
        pos = nx.spring_layout(subG, k=2.0/np.sqrt(max(subG.number_of_nodes(), 1)),
                               iterations=60, seed=42)
    elif layout_algo == "Kamada-Kawai":
        try:
            pos = nx.kamada_kawai_layout(subG)
        except Exception:
            pos = nx.spring_layout(subG, seed=42)
    elif layout_algo == "Circular":
        pos = nx.circular_layout(subG)
    else:
        pos = nx.shell_layout(subG)

    # ─── Build Plotly traces ─────────────────────────────────────────────────
    fig = go.Figure()

    # --- Edges ---
    max_delay = max((d.get('delay_ratio', 0) for _, _, d in subG.edges(data=True)), default=1)
    max_weight = max((d.get('weight', 1) for _, _, d in subG.edges(data=True)), default=1)

    for u, v, data in subG.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        dr = data.get('delay_ratio', 0)
        w = data.get('weight', 1)

        # Color by delay severity — muted tones for light background
        norm_delay = min(dr / max(max_delay, 0.01), 1.0)
        if norm_delay < 0.3:
            color = "rgba(21,128,61,0.5)"   # muted green
        elif norm_delay < 0.6:
            color = "rgba(180,83,9,0.5)"    # muted amber
        else:
            color = "rgba(185,28,28,0.6)"   # muted red

        width = max(0.5, min(4, w / max(max_weight, 1) * 4))

        fig.add_trace(go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            mode='lines',
            line=dict(width=width, color=color),
            hoverinfo='text',
            text=f"{u[-8:]} → {v[-8:]}<br>Trips: {w}<br>Delay: {dr:.2f}x",
            showlegend=False,
        ))

    # --- Nodes ---
    node_x, node_y, node_text, node_size, node_color = [], [], [], [], []
    for node in subG.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        bc = betweenness.get(node, 0)
        dc = degree_cent.get(node, 0)
        in_f = subG.nodes[node].get('in_flow', 0) if node in subG.nodes else 0
        out_f = subG.nodes[node].get('out_flow', 0) if node in subG.nodes else 0

        node_text.append(
            f"<b>{node}</b><br>"
            f"Betweenness: {bc:.5f}<br>"
            f"Degree Centrality: {dc:.4f}<br>"
            f"In-Flow: {in_f}<br>"
            f"Out-Flow: {out_f}<br>"
            f"Connections: {subG.degree(node)}"
        )
        node_size.append(max(8, bc * node_scale * 500))
        node_color.append(bc)

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        marker=dict(
            size=node_size,
            color=node_color,
            colorscale='RdBu_r',
            showscale=True,
            colorbar=dict(
                title=dict(text="Betweenness", font=dict(size=12, color=COLORS['text_muted'])),
                thickness=12,
                len=0.5,
                tickfont=dict(color=COLORS['text_muted']),
            ),
            line=dict(width=1, color='rgba(0,0,0,0.15)'),
        ),
        hoverinfo='text',
        text=[''] * len(node_x),
        hovertext=node_text,
        showlegend=False,
    ))

    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=650,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, gridcolor="rgba(0,0,0,0)"),
        title=dict(
            text=f"Logistics Network — {subG.number_of_nodes()} Hubs, {subG.number_of_edges()} Corridors",
            font=dict(size=16, color=COLORS['text_muted']),
            x=0.5,
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ─── Legend ──────────────────────────────────────────────────────────────
    render_insight(
        "<strong>How to read this graph:</strong> "
        "Node size reflects <strong>betweenness centrality</strong> — larger nodes are critical transit hubs. "
        "Edge color indicates <strong>delay severity</strong>: "
        '<span style="color:#22C55E">■ Low</span> · '
        '<span style="color:#F59E0B">■ Moderate</span> · '
        '<span style="color:#EF4444">■ High</span>. '
        "Edge thickness represents <strong>trip volume</strong>."
    )

    render_divider()

    # ─── Centrality Distribution ─────────────────────────────────────────────
    render_section_header("📈", "Centrality Distribution",
                          "Distribution of betweenness centrality across all hubs")
    col_a, col_b = st.columns(2)

    with col_a:
        bc_values = list(betweenness.values())
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=bc_values, nbinsx=40,
            marker_color=COLORS['primary'],
            opacity=0.85,
            hovertemplate="Centrality: %{x:.5f}<br>Hubs: %{y}<extra></extra>",
        ))
        fig_hist.update_layout(
            **PLOTLY_LAYOUT,
            height=350,
            xaxis_title="Betweenness Centrality",
            yaxis_title="Number of Hubs",
            showlegend=False,
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_b:
        # Degree distribution
        degrees = [d for _, d in subG.degree()]
        fig_deg = go.Figure()
        fig_deg.add_trace(go.Histogram(
            x=degrees, nbinsx=30,
            marker_color=COLORS['accent'],
            opacity=0.85,
            hovertemplate="Degree: %{x}<br>Hubs: %{y}<extra></extra>",
        ))
        fig_deg.update_layout(
            **PLOTLY_LAYOUT,
            height=350,
            xaxis_title="Node Degree (Connections)",
            yaxis_title="Number of Hubs",
            showlegend=False,
        )
        st.plotly_chart(fig_deg, use_container_width=True)
