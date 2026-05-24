"""
Data Loading & Caching Module
Handles all data loading with Streamlit caching for performance.
"""

import pandas as pd
import numpy as np
import streamlit as st
import networkx as nx
from config import (
    GRAPH_FEATURED_DATA, GRAPH_DATA, MODEL_COMPARISON,
    SLA_THRESHOLD, BOTTLENECK_THRESHOLD
)


@st.cache_data(ttl=3600, show_spinner=False)
def load_featured_data() -> pd.DataFrame:
    """Load the main graph-featured dataset with engineered features."""
    df = pd.read_csv(GRAPH_FEATURED_DATA, low_memory=False)

    # Ensure numeric columns
    numeric_cols = [
        'actual_time', 'osrm_time', 'actual_distance_to_destination',
        'osrm_distance', 'delay', 'delay_ratio', 'source_betweenness',
        'destination_betweenness', 'trip_hour', 'trip_day', 'trip_month',
        'segment_actual_time', 'segment_osrm_time', 'factor',
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Derive additional columns if not present
    if 'corridor_risk_score' not in df.columns:
        df['corridor_risk_score'] = df['delay_ratio'] * np.log1p(df.get('factor', df['delay_ratio']))

    if 'segment_delay_ratio' not in df.columns:
        if 'segment_actual_time' in df.columns and 'segment_osrm_time' in df.columns:
            df['segment_delay_ratio'] = df['segment_actual_time'] / df['segment_osrm_time'].replace(0, np.nan)
        else:
            df['segment_delay_ratio'] = df['delay_ratio']

    if 'avg_speed' not in df.columns:
        df['avg_speed'] = (
            df['actual_distance_to_destination'] /
            df['actual_time'].replace(0, np.nan) * 60  # km/h
        )

    if 'recommended_mode' not in df.columns:
        df['recommended_mode'] = np.where(
            (df['actual_distance_to_destination'] > 200) | (df['delay_ratio'] > SLA_THRESHOLD),
            'FTL', 'Carting'
        )

    # SLA breach flag
    df['sla_breach'] = (df['delay_ratio'] > SLA_THRESHOLD).astype(int)

    return df


@st.cache_data(ttl=3600, show_spinner=False)
def load_graph_data() -> pd.DataFrame:
    """Load aggregated graph/corridor-level data."""
    df = pd.read_csv(GRAPH_DATA)
    numeric_cols = ['delay_ratio', 'actual_time', 'osrm_time', 'trip_count', 'actual_distance_to_destination']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def load_model_comparison() -> pd.DataFrame:
    """Load ML model comparison results."""
    return pd.read_csv(MODEL_COMPARISON)


@st.cache_data(ttl=3600, show_spinner=False)
def build_network_graph(graph_df: pd.DataFrame):
    """Build a NetworkX graph from corridor data and compute centrality metrics."""
    G = nx.DiGraph()

    for _, row in graph_df.iterrows():
        src = row['source_center']
        dst = row['destination_center']
        G.add_edge(
            src, dst,
            weight=row.get('trip_count', 1),
            delay_ratio=row.get('delay_ratio', 0),
            actual_time=row.get('actual_time', 0),
            osrm_time=row.get('osrm_time', 0),
        )

    # Compute centrality metrics
    betweenness = nx.betweenness_centrality(G, weight='weight')
    degree_cent = nx.degree_centrality(G)
    in_degree = dict(G.in_degree(weight='weight'))
    out_degree = dict(G.out_degree(weight='weight'))

    # Attach as node attributes
    nx.set_node_attributes(G, betweenness, 'betweenness')
    nx.set_node_attributes(G, degree_cent, 'degree_centrality')
    nx.set_node_attributes(G, in_degree, 'in_flow')
    nx.set_node_attributes(G, out_degree, 'out_flow')

    return G, betweenness, degree_cent


def get_bottleneck_hubs(G, betweenness: dict, threshold: float = BOTTLENECK_THRESHOLD) -> pd.DataFrame:
    """Identify bottleneck hubs based on betweenness centrality."""
    values = list(betweenness.values())
    if not values:
        return pd.DataFrame()
    cutoff = np.quantile(values, threshold)
    bottlenecks = {k: v for k, v in betweenness.items() if v >= cutoff}

    records = []
    for hub, bc in sorted(bottlenecks.items(), key=lambda x: -x[1]):
        node_data = G.nodes[hub]
        # Compute average delay for edges involving this hub
        delays = []
        for _, _, data in G.edges(hub, data=True):
            delays.append(data.get('delay_ratio', 0))
        for _, _, data in G.in_edges(hub, data=True):
            delays.append(data.get('delay_ratio', 0))
        avg_delay = np.mean(delays) if delays else 0

        records.append({
            'hub': hub,
            'betweenness_centrality': round(bc, 6),
            'degree_centrality': round(node_data.get('degree_centrality', 0), 6),
            'in_flow': node_data.get('in_flow', 0),
            'out_flow': node_data.get('out_flow', 0),
            'total_flow': node_data.get('in_flow', 0) + node_data.get('out_flow', 0),
            'avg_delay_ratio': round(avg_delay, 3),
            'connected_corridors': G.degree(hub),
        })

    return pd.DataFrame(records)


def get_corridor_stats(graph_df: pd.DataFrame) -> pd.DataFrame:
    """Compute corridor-level statistics."""
    df = graph_df.copy()
    df['corridor'] = df['source_center'] + ' → ' + df['destination_center']
    df['risk_score'] = df['delay_ratio'] * np.log1p(df.get('trip_count', 1))
    df = df.sort_values('delay_ratio', ascending=False)
    return df


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply user-selected filters to the dataframe."""
    filtered = df.copy()

    if filters.get('source_hub') and filters['source_hub'] != 'All':
        filtered = filtered[filtered['source_center'] == filters['source_hub']]

    if filters.get('dest_hub') and filters['dest_hub'] != 'All':
        filtered = filtered[filtered['destination_center'] == filters['dest_hub']]

    if filters.get('route_type') and filters['route_type'] != 'All':
        if 'route_type' in filtered.columns:
            filtered = filtered[filtered['route_type'] == filters['route_type']]

    if filters.get('delay_threshold') is not None:
        filtered = filtered[filtered['delay_ratio'] >= filters['delay_threshold']]

    if filters.get('trip_hour') is not None and 'trip_hour' in filtered.columns:
        if isinstance(filters['trip_hour'], (list, tuple)):
            filtered = filtered[
                filtered['trip_hour'].between(filters['trip_hour'][0], filters['trip_hour'][1])
            ]

    if filters.get('risk_score') is not None:
        if 'corridor_risk_score' in filtered.columns:
            filtered = filtered[filtered['corridor_risk_score'] >= filters['risk_score']]

    return filtered
