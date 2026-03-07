# 🌊 Floodvision-Pro
### Ward-Level Urban Flood Intelligence & Digital Twin Platform

**A production-quality hackathon MVP aligned with Smart City ICCC standards.**

```
 ___  _____   _______ ____  ______ _____ ____  _   _ _____ __    ____   ___  ____  ____ 
/ __)(  _  ) (  __  )( ___)(  __ \(  ___)(_  _)( )_( )( ___)  ) ( __ ) / _ \( ___)(  _ \
\__ \ )(_)(  )(  )(   )__)  )  ) / )__)  _(  )_ )   (  )__)  )(  (_ ( ) (_) ))__)  )(_) )
(___/(_____)  (____)  (____)  (__/  (____)(____)(_)_(_)(__)   (__)(___/ \___/(____)  (__/
```

---

## 🎯 Overview

Floodvision-Pro is a GIS-integrated decision-support system that enables Indian municipalities to:

| Module | Purpose |
|--------|---------|
| **Micro Flood Hotspot Engine** | Detect hyperlocal flood-prone zones using DEM + rainfall analysis |
| **Drain Failure Intelligence** | Predict clogged/weak drains via multi-factor health scoring |
| **Ward Readiness Score** | Composite pre-monsoon preparedness metric (0–100) |
| **Flood-Aware Route Engine** | Compute safest emergency routes using NetworkX graph |
| **Budget Impact Optimizer** | Greedy knapsack optimization for intervention planning |
| **Digital Twin Simulator** | Real-time what-if simulation with map feedback |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (HTML+JS)                   │
│   Leaflet Map │ Chart.js │ ICCC Dark Dashboard          │
└───────────────────────┬─────────────────────────────────┘
                        │ REST API (JSON)
┌───────────────────────▼─────────────────────────────────┐
│                FastAPI Backend                          │
│                                                         │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │  Hotspot   │  │    Drain     │  │  Ward          │  │
│  │  Engine    │  │  Intelligence│  │  Readiness     │  │
│  └────────────┘  └──────────────┘  └────────────────┘  │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │   Route    │  │   Budget     │  │  Digital Twin  │  │
│  │   Engine   │  │  Optimizer   │  │  Simulator     │  │
│  └────────────┘  └──────────────┘  └────────────────┘  │
│                                                         │
│  Data Layer: NumPy DEM │ Rainfall Grid │ NetworkX Graph │
└─────────────────────────────────────────────────────────┘
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- `pip`
- A modern browser

### 1. Clone / extract the project

```bash
cd FloodVision-Pro
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be live at: **http://localhost:8000**

Interactive docs: **http://localhost:8000/docs**

### 3. Frontend Setup

```bash
cd frontend

# Serve with any static server:
python -m http.server 3000
# OR
npx serve .
```

Open **http://localhost:3000** in your browser.

---

## 📡 API Reference

### GET /hotspots
Returns GeoJSON heatmap of flood-prone zones.
```bash
curl http://localhost:8000/hotspots
```
Response:
```json
{
  "type": "FeatureCollection",
  "features": [...],
  "metadata": {
    "total_hotspots": 52,
    "high_risk_count": 14,
    "medium_risk_count": 23,
    "low_risk_count": 15
  }
}
```

### GET /drain-health
Drain Health Index for every drain segment.
```bash
curl http://localhost:8000/drain-health
```

### GET /ward-readiness
Pre-monsoon readiness score per ward.
```bash
curl http://localhost:8000/ward-readiness
```

### POST /safe-route
Compute flood-avoiding emergency route.
```bash
curl -X POST http://localhost:8000/safe-route \
  -H "Content-Type: application/json" \
  -d '{"source_lat":21.142,"source_lon":79.085,"dest_lat":21.165,"dest_lon":79.112}'
```

### POST /optimize-budget
Budget allocation optimizer (₹10M example):
```bash
curl -X POST http://localhost:8000/optimize-budget \
  -H "Content-Type: application/json" \
  -d '{"total_budget": 10000000}'
```

### POST /simulate
Digital Twin simulation:
```bash
curl -X POST http://localhost:8000/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "ward_id": "W01",
    "drain_cleaning": 0.8,
    "pump_deployment": 0.5,
    "new_drain": 0.3,
    "road_fix": 0.2
  }'
```

---

## 🎬 Demo Flow (For Judges)

1. **Open the dashboard** → observe ICCC-style dark map with ward choropleth
2. **Layer toggles** (left sidebar) → switch flood hotspots, drain health, ward readiness
3. **Click any ward** on the map → Ward Detail panel opens with radar chart + priority actions
4. **Digital Twin** → select a High Risk ward (red), move sliders to 80%+
   - Watch the readiness score jump live
   - Flood hotspots downgrade visibly on the map
5. **Safe Route** (bottom-right) → hit "Compute Safe Route" → cyan route avoids red zones
6. **Budget Optimizer** tab → enter ₹50,000,000 → see ranked intervention table + bar chart

---

## 🗂️ Project Structure

```
FloodVision-Pro/
├── backend/
│   ├── main.py                    # FastAPI app + endpoints
│   ├── requirements.txt
│   └── services/
│       ├── __init__.py
│       ├── data_generator.py      # Synthetic ward/drain/road/DEM data
│       ├── hotspot_engine.py      # MODULE 1 — Flood Hotspot Engine
│       ├── drain_intelligence.py  # MODULE 2 — Drain Failure Intelligence
│       ├── ward_readiness.py      # MODULE 3 — Ward Readiness Score
│       ├── route_engine.py        # MODULE 4 — Safe Route Engine
│       ├── budget_optimizer.py    # MODULE 5 — Budget Optimizer
│       └── digital_twin.py        # MODULE 6 — Digital Twin Simulator
│
├── frontend/
│   └── index.html                 # Complete ICCC dashboard (single-file)
│
└── README.md
```

---

## 🛠️ Technical Notes

- **Data**: All data is synthetic but calibrated to real-world Nagpur-like city geometry
- **DEM**: 20×20 NumPy grid with realistic terrain depressions
- **Road Graph**: NetworkX grid graph (5×4 ward grid → ~50 road segments)
- **Routing**: Dijkstra's algorithm with flood-zone edge weight penalties (8× multiplier)
- **Budget**: Greedy knapsack sorted by readiness_gain/cost efficiency ratio
- **Digital Twin**: Real-time effect models with sub-second response

---

## 📋 Score Bands

| Metric | Green | Amber | Red |
|--------|-------|-------|-----|
| Ward Readiness | 80–100 Ready | 60–79 Moderate | <60 High Risk |
| Drain Health | 80–100 Healthy | 50–79 Moderate | <50 High Risk |
| Hotspot Risk | Low | Medium | High |

---

*Built for Smart City ICCC Hackathon — Nagpur Municipal Corporation Flood Preparedness 2025*
