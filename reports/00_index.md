# ETA Optimization — Reports Index

> **Delhivery Graph-Based Network Intelligence Project**
> All findings, code documentation, model results, and operational recommendations in one organized place.

---

##  Report Directory

| # | Report | Description |
|---|--------|-------------|
| 1 | [01_data_pipeline_and_graph_construction.md](01_data_pipeline_and_graph_construction.md) | Data pipeline design, graph construction methodology, feature engineering |
| 2 | [02_bottleneck_and_corridor_audit.md](02_bottleneck_and_corridor_audit.md) | Centrality analysis, SLA breach attribution, corridor delay rankings |
| 3 | [03_graph_enhanced_eta_model.md](03_graph_enhanced_eta_model.md) | Baseline vs graph-enhanced model benchmarking, "graph advantage" measurement |
| 4 | [04_ftl_vs_carting_framework.md](04_ftl_vs_carting_framework.md) | ML-backed route-type decision framework with cost-time trade-off analysis |
| 5 | [05_network_operations_strategy_memo.md](05_network_operations_strategy_memo.md) | Executive memo — top 5 hubs, corridor interventions, revenue impact |
| — | [model_comparison.csv](model_comparison.csv) | Raw model performance metrics (Baseline vs Graph-Enhanced) |

---

##  Project at a Glance

```
Dataset       : Delhivery-inspired logistics data — 2,783 corridors, 300K+ trips
Graph         : Directed weighted graph (NetworkX) — hubs as nodes, corridors as edges
Features      : Betweenness centrality, corridor risk score, segment delay ratio
Models        : Baseline (XGBoost/LightGBM) vs Graph-Enhanced (+ graph features)
Dashboard     : 7-page Streamlit analytics platform
```

---

##  Key Results Summary

| Metric | Value |
|--------|-------|
| **Baseline MAE** | 5.94 min |
| **Graph-Enhanced MAE** | 5.68 min (−4.2%) |
| **Baseline RMSE** | 14.48 min |
| **Graph-Enhanced RMSE** | 13.77 min (−4.9%) |
| **Baseline Accuracy ±15%** | 99.20% |
| **Graph-Enhanced Accuracy ±15%** | 99.31% (+0.11 pp) |
| **Estimated SLA breach reduction** | 20–35% (combined interventions) |
| **Estimated cost reduction** | ~32% (combined interventions) |

---

##  Related Files

- **Interactive Dashboard**: `dashboard/app.py` — run with `streamlit run dashboard/app.py`
- **Notebooks**: `notebooks/01` through `05` — full analytical pipeline
- **Models**: `models/baseline_model.joblib`, `models/graph_model.joblib`
- **Data**: `data/cleaned/` — cleaned trip data, graph edge data, graph-featured data
