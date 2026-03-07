"""
SovereignFlood — Synthetic Data Generator
Generates realistic ward/drain/road data for a hypothetical Indian city (Nagpur-like grid)
"""

import numpy as np
import json
from typing import List, Dict, Any

# City center (Nagpur approximate)
CITY_CENTER = (21.1458, 79.0882)
GRID_ROWS = 4
GRID_COLS = 5
WARD_SPACING = 0.025  # ~2.75 km per ward

def generate_ward_boundaries() -> List[Dict[str, Any]]:
    """Generate 20 synthetic ward polygons in a grid layout."""
    wards = []
    lat0, lon0 = CITY_CENTER[0] - 0.05, CITY_CENTER[1] - 0.0625
    
    ward_names = [
        "Gandhibagh", "Lakadganj", "Sadar", "Civil Lines", "Sitabuldi",
        "Dhantoli", "Dharampeth", "Ramdaspeth", "Wardhaman Nagar", "Pratap Nagar",
        "Nandanvan", "Manish Nagar", "Sakkardara", "Kalamna", "Besa",
        "Hudkeshwar", "Wathoda", "Kamptee Road", "Hingna Road", "Khapri"
    ]
    
    risk_profile = [
        0.82, 0.45, 0.91, 0.33, 0.76,
        0.58, 0.40, 0.35, 0.68, 0.55,
        0.72, 0.63, 0.88, 0.79, 0.41,
        0.66, 0.84, 0.74, 0.61, 0.47
    ]

    idx = 0
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            lat = lat0 + r * WARD_SPACING
            lon = lon0 + c * WARD_SPACING
            s = WARD_SPACING

            ward_id = f"W{idx+1:02d}"
            wards.append({
                "type": "Feature",
                "properties": {
                    "ward_id": ward_id,
                    "ward_name": ward_names[idx],
                    "flood_risk_base": risk_profile[idx],
                    "population": int(np.random.uniform(25000, 85000)),
                    "area_sqkm": round(np.random.uniform(3.2, 8.7), 2),
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [lon,       lat],
                        [lon + s,   lat],
                        [lon + s,   lat + s],
                        [lon,       lat + s],
                        [lon,       lat],
                    ]]
                }
            })
            idx += 1

    return wards


def generate_drain_network(wards: List[Dict]) -> List[Dict[str, Any]]:
    """Generate synthetic drain lines across ward areas."""
    drains = []
    drain_id = 1

    for ward in wards:
        coords = ward["geometry"]["coordinates"][0]
        lat0 = coords[0][1]
        lon0 = coords[0][0]
        s = WARD_SPACING
        flood_risk = ward["properties"]["flood_risk_base"]

        # 3–5 drain segments per ward
        n_drains = np.random.randint(3, 6)
        for i in range(n_drains):
            start_lat = lat0 + np.random.uniform(0.002, s - 0.002)
            start_lon = lon0 + np.random.uniform(0.002, s - 0.002)
            end_lat = start_lat + np.random.uniform(-0.008, 0.008)
            end_lon = start_lon + np.random.uniform(0.002, 0.012)

            # Health score inversely correlated with flood risk + noise
            base_health = (1 - flood_risk) * 100
            health_score = float(np.clip(base_health + np.random.normal(0, 12), 5, 100))

            drains.append({
                "type": "Feature",
                "properties": {
                    "drain_id": f"D{drain_id:03d}",
                    "ward_id": ward["properties"]["ward_id"],
                    "drain_type": np.random.choice(["open", "covered", "stormwater"]),
                    "age_years": int(np.random.uniform(5, 35)),
                    "last_cleaned_days": int(np.random.uniform(10, 400)),
                    "health_score_base": round(health_score, 1),
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [start_lon, start_lat],
                        [end_lon, end_lat]
                    ]
                }
            })
            drain_id += 1

    return drains


def generate_road_network() -> List[Dict[str, Any]]:
    """Generate synthetic road grid for routing."""
    roads = []
    lat0, lon0 = CITY_CENTER[0] - 0.05, CITY_CENTER[1] - 0.0625
    road_id = 1

    # Horizontal roads
    for r in range(GRID_ROWS + 1):
        lat = lat0 + r * WARD_SPACING
        for c in range(GRID_COLS):
            lon_s = lon0 + c * WARD_SPACING
            lon_e = lon_s + WARD_SPACING
            roads.append({
                "road_id": f"R{road_id:03d}",
                "road_type": "arterial" if r % 2 == 0 else "secondary",
                "start": [lon_s, lat],
                "end": [lon_e, lat],
            })
            road_id += 1

    # Vertical roads
    for c in range(GRID_COLS + 1):
        lon = lon0 + c * WARD_SPACING
        for r in range(GRID_ROWS):
            lat_s = lat0 + r * WARD_SPACING
            lat_e = lat_s + WARD_SPACING
            roads.append({
                "road_id": f"R{road_id:03d}",
                "road_type": "arterial" if c % 2 == 0 else "secondary",
                "start": [lon, lat_s],
                "end": [lon, lat_e],
            })
            road_id += 1

    return roads


def generate_mock_dem() -> np.ndarray:
    """Generate mock DEM elevation grid (20x20 cells)."""
    np.random.seed(42)
    dem = np.random.normal(315, 12, (20, 20)).astype(np.float32)
    # Add a low-lying basin (flood prone area)
    dem[6:10, 2:6] -= 18
    dem[12:16, 8:13] -= 14
    return dem


def generate_rainfall_grid() -> np.ndarray:
    """Generate mock monsoon rainfall anomaly grid (mm above normal)."""
    np.random.seed(7)
    base = np.random.normal(85, 22, (20, 20)).astype(np.float32)
    # Hotspots
    base[6:10, 2:6] += 45
    base[12:16, 8:13] += 35
    return base
