"""
SovereignFlood - Ward-Level Urban Flood Intelligence Platform
FastAPI Backend — Production MVP
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json

from services.hotspot_engine import HotspotEngine
from services.drain_intelligence import DrainIntelligence
from services.ward_readiness import WardReadiness
from services.route_engine import RouteEngine
from services.budget_optimizer import BudgetOptimizer
from services.digital_twin import DigitalTwin

app = FastAPI(
    title="SovereignFlood API",
    description="Ward-Level Urban Flood Intelligence & Digital Twin Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (singleton pattern)
hotspot_engine = HotspotEngine()
drain_intel = DrainIntelligence()
ward_readiness = WardReadiness()
route_engine = RouteEngine()
budget_optimizer = BudgetOptimizer()
digital_twin = DigitalTwin()


# ── Request/Response Models ──────────────────────────────────────────────────

class RouteRequest(BaseModel):
    source_lat: float
    source_lon: float
    dest_lat: float
    dest_lon: float

class BudgetRequest(BaseModel):
    total_budget: float

class SimulateRequest(BaseModel):
    ward_id: str
    drain_cleaning: float = 0.0      # 0–1
    pump_deployment: float = 0.0     # 0–1
    new_drain: float = 0.0           # 0–1
    road_fix: float = 0.0            # 0–1


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "operational", "system": "SovereignFlood ICCC Platform v1.0"}

@app.get("/hotspots")
def get_hotspots():
    """MODULE 1 — Micro Flood Hotspot Engine"""
    return hotspot_engine.get_hotspots()

@app.get("/drain-health")
def get_drain_health():
    """MODULE 2 — Last-Meter Drain Failure Intelligence"""
    return drain_intel.get_drain_health()

@app.get("/ward-readiness")
def get_ward_readiness():
    """MODULE 3 — Ward Pre-Monsoon Readiness Score"""
    return ward_readiness.get_readiness()

@app.post("/safe-route")
def compute_safe_route(req: RouteRequest):
    """MODULE 4 — Flood-Aware Critical Route Engine"""
    return route_engine.compute_safe_route(
        req.source_lat, req.source_lon,
        req.dest_lat, req.dest_lon
    )

@app.post("/optimize-budget")
def optimize_budget(req: BudgetRequest):
    """MODULE 5 — Budget Impact Optimizer"""
    return budget_optimizer.optimize(req.total_budget)

@app.post("/simulate")
def simulate(req: SimulateRequest):
    """MODULE 6 — Digital Twin What-If Simulator"""
    return digital_twin.simulate(
        ward_id=req.ward_id,
        drain_cleaning=req.drain_cleaning,
        pump_deployment=req.pump_deployment,
        new_drain=req.new_drain,
        road_fix=req.road_fix
    )

@app.get("/health")
def health():
    return {"status": "healthy", "modules": 6, "data_loaded": True}
