# Report 1 — Data Pipeline & Graph Construction

**Project:** ETA Optimization using Graph-Based Network Intelligence
**Date:** May 2024
**Notebook:** `notebooks/04_graph_construction.ipynb`

---

## 1. Overview

This report documents the end-to-end data pipeline used to transform raw Delhivery-inspired trip segment data into a directed weighted graph suitable for graph-analytics and ML-based ETA prediction. Every design choice is justified below — the goal is reproducibility and transparency, not just code that runs.

---

## 2. Raw Data Schema

The raw dataset contains individual trip segment records, one row per segment leg, with the following key fields:

| Field | Type | Description |
|-------|------|-------------|
| `trip_uuid` | string | Unique trip identifier |
| `source_center` | string | Originating facility code |
| `destination_center` | string | Destination facility code |
| `route_type` | string | `FTL` (Full Truck Load) or `Carting` |
| `actual_time` | float | Actual transit time (minutes) |
| `osrm_time` | float | OSRM-predicted time (minutes) |
| `actual_distance_to_destination` | float | Actual distance (km) |
| `osrm_distance` | float | OSRM-predicted distance (km) |
| `trip_creation_time` | datetime | Timestamp of trip creation |
| `od_start_time` | datetime | Segment departure timestamp |
| `od_end_time` | datetime | Segment arrival timestamp |

> [!NOTE]
> OSRM (Open Source Routing Machine) provides baseline routing estimates assuming no congestion. The gap between `actual_time` and `osrm_time` is the primary signal for delay modeling.

---

## 3. Data Cleaning Pipeline

### 3.1 Null & Consistency Checks

**File:** `notebooks/02_data_cleaning.ipynb`

```python
# Drop rows with missing core fields
df = df.dropna(subset=[
    'source_center', 'destination_center',
    'actual_time', 'osrm_time',
    'actual_distance_to_destination'
])

# Remove physically impossible values
df = df[df['actual_time'] > 0]
df = df[df['osrm_time'] > 0]
df = df[df['actual_distance_to_destination'] > 0]
```

**Why not impute?** Trip time and distance are the primary modeling targets. Imputing them would introduce systematic bias into delay ratio computations, corrupting the very features the model depends on. Removal is safer here.

### 3.2 Outlier Treatment

Delay ratios above the 99.9th percentile (~10×) represent data errors or extraordinary events (road closures, accidents) that are not generalizable. These are capped rather than dropped to preserve row count while limiting leverage:

```python
df['delay_ratio'] = df['actual_time'] / df['osrm_time']
cap_value = df['delay_ratio'].quantile(0.999)
df['delay_ratio'] = df['delay_ratio'].clip(upper=cap_value)
```

**Justification:** Capping (Winsorization) retains the full sample size while preventing extreme outliers from dominating gradient-based models. Hard dropping would reduce data by ~0.1% but risk removing valid high-delay records near the threshold.

### 3.3 Feature Engineering

**File:** `notebooks/03_feature_engineering_eda.ipynb`

```python
# Time-of-day features
df['trip_hour'] = pd.to_datetime(df['od_start_time']).dt.hour
df['trip_day_of_week'] = pd.to_datetime(df['od_start_time']).dt.dayofweek
df['is_peak_hour'] = df['trip_hour'].isin([8,9,10,17,18,19,20]).astype(int)

# Speed feature
df['avg_speed'] = df['actual_distance_to_destination'] / (df['actual_time'] / 60)

# SLA breach flag
SLA_THRESHOLD = 1.5
df['sla_breach'] = (df['delay_ratio'] > SLA_THRESHOLD).astype(int)
```

---

## 4. Graph Construction

### 4.1 Design Rationale — Why a Directed Graph?

Logistics networks are **inherently directional** — a trip from Mumbai to Delhi is operationally different from Delhi to Mumbai in terms of congestion patterns, load factors, and hub dwell times. Using an undirected graph would mask these asymmetries.

**Model choice:** `networkx.DiGraph` — a directed graph that supports:
- Per-edge weight attributes (delay ratio, trip count)
- Centrality metrics on directed networks (betweenness, in/out-degree)
- Efficient subgraph extraction for visualization

### 4.2 Edge Construction

Each unique `(source_center, destination_center)` pair with matching `route_type` and `trip_hour` bucket becomes an **edge** in the graph. Edge weights are aggregated statistics over all trips on that corridor.

```python
# Aggregate trips by corridor
graph_df = df.groupby(['source_center', 'destination_center', 'route_type']).agg(
    trip_count=('trip_uuid', 'count'),
    median_delay_ratio=('delay_ratio', 'median'),   # median — robust to skew
    mean_delay_ratio=('delay_ratio', 'mean'),
    sla_breach_rate=('sla_breach', 'mean'),
    avg_distance=('actual_distance_to_destination', 'mean'),
    avg_actual_time=('actual_time', 'mean'),
).reset_index()

# Corridor risk score — combines delay severity with volume
graph_df['corridor_risk_score'] = (
    graph_df['median_delay_ratio'] * np.log1p(graph_df['trip_count'])
)
```

**Why median for delay ratio?** The delay ratio distribution is right-skewed (long tail of high-delay events). The median is more robust to these extremes and better represents the "typical" corridor experience. The mean is also retained for reference.

**Why `log1p(trip_count)` for risk score?** Raw trip count can dominate the risk score on high-volume corridors. Logarithmic scaling ensures that a corridor with 1,000 trips and delay ratio 2.0 is not automatically ranked higher than one with 100 trips and delay ratio 3.0 — the delay severity still matters.

### 4.3 Graph Assembly

```python
import networkx as nx

G = nx.DiGraph()

# Add edges with weight attributes
for _, row in graph_df.iterrows():
    G.add_edge(
        row['source_center'],
        row['destination_center'],
        weight=row['trip_count'],             # primary edge weight
        delay_ratio=row['median_delay_ratio'],
        risk_score=row['corridor_risk_score'],
        route_type=row['route_type'],
        sla_breach_rate=row['sla_breach_rate'],
    )
```

### 4.4 Time-of-Day Stratification

Delay ratios are stratified by hour bucket (Morning: 6–12, Afternoon: 12–17, Evening: 17–22, Night: 22–6) to capture congestion patterns. This stratification is used for time-aware routing recommendations but the base graph uses all-hours aggregates for centrality computation.

```python
TIME_BUCKETS = {
    'morning':   range(6, 12),
    'afternoon': range(12, 17),
    'evening':   range(17, 22),
    'night':     list(range(22, 24)) + list(range(0, 6)),
}

df['time_bucket'] = df['trip_hour'].apply(
    lambda h: next((k for k, v in TIME_BUCKETS.items() if h in v), 'night')
)
```

---

## 5. Graph-Level Feature Computation

### 5.1 Betweenness Centrality

```python
betweenness = nx.betweenness_centrality(G, weight='weight', normalized=True)
```

**Interpretation:** A hub with high betweenness centrality lies on many shortest paths in the network. Delays at such a hub propagate to a disproportionate number of downstream trips.

**Normalization:** Values are normalized to [0,1] so they are scale-invariant and directly usable as ML features.

### 5.2 Degree Centrality

```python
in_degree  = nx.in_degree_centrality(G)
out_degree = nx.out_degree_centrality(G)
```

In-degree = number of corridors feeding into a hub (inbound pressure). Out-degree = number of corridors leaving (dispatch capacity).

### 5.3 Clustering Coefficient

```python
clustering = nx.clustering(G.to_undirected())
```

High clustering around a hub indicates many triangulated routes — these hubs are locally critical and difficult to bypass.

---

## 6. Graph-Enhanced Feature Join

Graph features are joined back to the trip-level dataset for ML modeling:

```python
df['source_betweenness']      = df['source_center'].map(betweenness)
df['destination_betweenness'] = df['destination_center'].map(betweenness)
df['source_in_degree']        = df['source_center'].map(in_degree)
df['source_out_degree']       = df['source_center'].map(out_degree)

# Corridor-level risk score join
corridor_risk = graph_df.set_index(['source_center','destination_center'])['corridor_risk_score']
df['corridor_risk_score'] = df.set_index(
    ['source_center','destination_center']
).index.map(corridor_risk)

# Segment delay ratio (per-leg actual vs OSRM)
df['segment_delay_ratio'] = df['actual_time'] / df['osrm_time']
```

**Output:** `data/cleaned/graph_featured_data.csv` — the full trip dataset with graph features, ready for ML modeling.

---

## 7. Graph Statistics

| Metric | Value |
|--------|-------|
| **Nodes (hubs)** | Computed dynamically from graph |
| **Edges (corridors)** | 2,783 |
| **Network density** | Sparse (typical of logistics networks) |
| **Top hub by betweenness** | Identified in Report 2 |
| **Avg clustering coefficient** | Computed dynamically |

---

## 8. Reproducibility Notes

- All random seeds fixed (`seed=42`) where applicable
- Data cleaning steps are deterministic (no random sampling)
- Graph construction is fully deterministic given the input CSV
- Output files: `data/cleaned/cleaned_data.csv`, `data/cleaned/graph_data.csv`, `data/cleaned/graph_featured_data.csv`

---

## 9. Pipeline Summary

```
Raw CSV
  │
  ├── Null removal & impossible-value filtering
  ├── Outlier capping (Winsorization at 99.9th percentile)
  ├── Feature engineering (delay_ratio, avg_speed, time features, SLA breach flag)
  │
  ├── Corridor aggregation → graph_data.csv
  │     - Median delay ratio per corridor (robust to skew)
  │     - Trip count as edge weight
  │     - Corridor risk score = delay_ratio × log1p(trip_count)
  │
  ├── Graph construction (NetworkX DiGraph)
  │     - Directed (asymmetric delays preserved)
  │     - Edge weights = trip count
  │
  ├── Centrality computation
  │     - Betweenness centrality (normalized)
  │     - In/Out degree centrality
  │     - Clustering coefficient
  │
  └── Feature join → graph_featured_data.csv
        - Graph features appended to each trip record
        - Used directly in ML modeling pipeline
```

---

*→ Continue to [Report 2: Bottleneck & Corridor Audit](02_bottleneck_and_corridor_audit.md)*
