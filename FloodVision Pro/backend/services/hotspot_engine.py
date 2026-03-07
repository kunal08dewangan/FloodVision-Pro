"""
MODULE 1 — Micro Flood Hotspot Engine
Detects hyperlocal flood-prone zones using DEM + rainfall proxies.
"""

import numpy as np
from typing import Dict, Any, List
from .data_generator import (
    generate_ward_boundaries, generate_mock_dem,
    generate_rainfall_grid, CITY_CENTER, WARD_SPACING, GRID_ROWS, GRID_COLS
)


class HotspotEngine:
    """Computes flood risk heatmap using DEM depression analysis + rainfall."""

    def __init__(self):
        self.wards = generate_ward_boundaries()
        self.dem = generate_mock_dem()        # 20×20 elevation grid
        self.rainfall = generate_rainfall_grid()  # 20×20 rainfall anomaly
        self._hotspots_cache = None

    def _compute_runoff_score(self, dem: np.ndarray, rainfall: np.ndarray) -> np.ndarray:
        """
        Simplified runoff proxy:
          runoff = rainfall * (1 - exp(-slope_factor)) + depression_depth_norm
        Depression = local cell below 5-cell neighbourhood mean.
        """
        from scipy.ndimage import uniform_filter
        smoothed = uniform_filter(dem.astype(float), size=3)
        depression = np.clip(smoothed - dem, 0, None)  # positive → depression
        depression_norm = depression / (depression.max() + 1e-6)

        rain_norm = (rainfall - rainfall.min()) / (rainfall.max() - rainfall.min() + 1e-6)
        runoff = 0.55 * rain_norm + 0.45 * depression_norm
        return runoff

    def _grid_to_latlon(self, row: int, col: int) -> tuple:
        """Convert 20×20 grid cell to approximate lat/lon center."""
        lat0 = CITY_CENTER[0] - 0.05
        lon0 = CITY_CENTER[1] - 0.0625
        total_lat = GRID_ROWS * WARD_SPACING
        total_lon = GRID_COLS * WARD_SPACING
        cell_lat = total_lat / 20
        cell_lon = total_lon / 20
        lat = lat0 + (row + 0.5) * cell_lat
        lon = lon0 + (col + 0.5) * cell_lon
        return lat, lon

    def _classify(self, score: float) -> str:
        if score >= 0.65:
            return "High"
        elif score >= 0.35:
            return "Medium"
        return "Low"

    def compute_hotspots(self) -> List[Dict[str, Any]]:
        """Return list of hotspot features with risk scores."""
        runoff = self._compute_runoff_score(self.dem, self.rainfall)
        hotspots = []
        threshold = 0.3  # show cells above this score

        for r in range(20):
            for c in range(20):
                score = float(runoff[r, c])
                if score < threshold:
                    continue
                lat, lon = self._grid_to_latlon(r, c)
                lat_span = (GRID_ROWS * WARD_SPACING) / 20 / 2
                lon_span = (GRID_COLS * WARD_SPACING) / 20 / 2
                hotspots.append({
                    "type": "Feature",
                    "properties": {
                        "hotspot_id": f"H{r:02d}{c:02d}",
                        "risk_score": round(score, 3),
                        "risk_category": self._classify(score),
                        "estimated_depth_m": round(score * 1.8, 2),
                        "rainfall_anomaly_mm": round(float(self.rainfall[r, c]), 1),
                        "elevation_m": round(float(self.dem[r, c]), 1),
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [lon - lon_span, lat - lat_span],
                            [lon + lon_span, lat - lat_span],
                            [lon + lon_span, lat + lat_span],
                            [lon - lon_span, lat + lat_span],
                            [lon - lon_span, lat - lat_span],
                        ]]
                    }
                })

        return hotspots

    def get_hotspots(self) -> Dict[str, Any]:
        """API response: GeoJSON FeatureCollection + summary stats."""
        if self._hotspots_cache is None:
            features = self.compute_hotspots()
            self._hotspots_cache = features

        features = self._hotspots_cache
        count_by_cat = {"High": 0, "Medium": 0, "Low": 0}
        for f in features:
            count_by_cat[f["properties"]["risk_category"]] += 1

        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "total_hotspots": len(features),
                "high_risk_count": count_by_cat["High"],
                "medium_risk_count": count_by_cat["Medium"],
                "low_risk_count": count_by_cat["Low"],
                "analysis_timestamp": "2025-06-15T08:00:00Z",
            }
        }

    def get_high_risk_cells(self) -> List[tuple]:
        """Return (lat, lon) of high-risk cells for routing penalty."""
        features = self._hotspots_cache or self.compute_hotspots()
        result = []
        for f in features:
            if f["properties"]["risk_category"] == "High":
                coords = f["geometry"]["coordinates"][0]
                lats = [c[1] for c in coords]
                lons = [c[0] for c in coords]
                result.append((
                    sum(lats) / len(lats),
                    sum(lons) / len(lons)
                ))
        return result
