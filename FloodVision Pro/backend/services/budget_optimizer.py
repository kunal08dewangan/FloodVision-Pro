"""
MODULE 5 — Budget Impact Optimizer
Ranks ward interventions by marginal readiness gain per rupee (greedy knapsack).
"""

import numpy as np
from typing import Dict, Any, List
from .ward_readiness import WardReadiness


INTERVENTION_CATALOG = [
    {
        "id": "drain_desilting",
        "name": "Primary Drain Desilting",
        "cost_inr": 850_000,
        "readiness_gain": 12.5,
        "flood_risk_reduction_pct": 18,
        "duration_days": 7,
        "category": "Drainage",
    },
    {
        "id": "pump_deployment",
        "name": "Submersible Pump Deployment (4 units)",
        "cost_inr": 1_200_000,
        "readiness_gain": 9.0,
        "flood_risk_reduction_pct": 14,
        "duration_days": 3,
        "category": "Emergency Equipment",
    },
    {
        "id": "culvert_repair",
        "name": "Culvert Repair & Enlargement",
        "cost_inr": 650_000,
        "readiness_gain": 7.5,
        "flood_risk_reduction_pct": 11,
        "duration_days": 14,
        "category": "Infrastructure",
    },
    {
        "id": "sensor_network",
        "name": "IoT Flood Sensor Network (10 nodes)",
        "cost_inr": 420_000,
        "readiness_gain": 5.0,
        "flood_risk_reduction_pct": 6,
        "duration_days": 5,
        "category": "Technology",
    },
    {
        "id": "nala_dredging",
        "name": "Nala Dredging & Bank Reinforcement",
        "cost_inr": 2_100_000,
        "readiness_gain": 18.0,
        "flood_risk_reduction_pct": 28,
        "duration_days": 21,
        "category": "Drainage",
    },
    {
        "id": "stormwater_aug",
        "name": "Stormwater Drain Augmentation",
        "cost_inr": 3_500_000,
        "readiness_gain": 22.0,
        "flood_risk_reduction_pct": 32,
        "duration_days": 45,
        "category": "Infrastructure",
    },
    {
        "id": "road_elevation",
        "name": "Critical Road Elevation Bunds",
        "cost_inr": 480_000,
        "readiness_gain": 4.5,
        "flood_risk_reduction_pct": 8,
        "duration_days": 10,
        "category": "Roads",
    },
    {
        "id": "manhole_replacement",
        "name": "Manhole Cover Audit & Replacement",
        "cost_inr": 180_000,
        "readiness_gain": 3.0,
        "flood_risk_reduction_pct": 4,
        "duration_days": 4,
        "category": "Maintenance",
    },
]


class BudgetOptimizer:
    """Greedy budget allocation optimizer for flood preparedness interventions."""

    def __init__(self):
        self.ward_readiness = WardReadiness()

    def optimize(self, total_budget: float) -> Dict[str, Any]:
        """
        Greedy knapsack: rank by readiness_gain / cost, allocate until budget exhausted.
        Prioritizes low-readiness wards.
        """
        ward_data = self.ward_readiness.get_ward_readiness_map()

        # Sort wards by readiness (lowest first — most need)
        sorted_wards = sorted(ward_data.items(), key=lambda x: x[1]["readiness_score"])

        # Compute efficiency ratio for interventions
        interventions_with_ratio = sorted(
            INTERVENTION_CATALOG,
            key=lambda x: x["readiness_gain"] / x["cost_inr"],
            reverse=True
        )

        allocated: List[Dict[str, Any]] = []
        remaining_budget = total_budget
        total_readiness_gain = 0.0
        total_risk_reduction = 0.0

        # Assign interventions to wards greedily
        for ward_id, ward_info in sorted_wards[:15]:  # top 15 most needy wards
            for intv in interventions_with_ratio[:3]:  # top 3 most efficient interventions per ward
                if remaining_budget >= intv["cost_inr"]:
                    allocated.append({
                        "ward_id": ward_id,
                        "ward_name": ward_info["ward_name"],
                        "current_readiness": ward_info["readiness_score"],
                        "intervention": intv["name"],
                        "intervention_id": intv["id"],
                        "category": intv["category"],
                        "cost_inr": intv["cost_inr"],
                        "cost_display": f"₹{intv['cost_inr']:,.0f}",
                        "readiness_gain": intv["readiness_gain"],
                        "projected_readiness": min(100, ward_info["readiness_score"] + intv["readiness_gain"]),
                        "flood_risk_reduction_pct": intv["flood_risk_reduction_pct"],
                        "duration_days": intv["duration_days"],
                        "efficiency_ratio": round(intv["readiness_gain"] / intv["cost_inr"] * 1e6, 3),
                    })
                    remaining_budget -= intv["cost_inr"]
                    total_readiness_gain += intv["readiness_gain"]
                    total_risk_reduction += intv["flood_risk_reduction_pct"]

                if remaining_budget < min(i["cost_inr"] for i in interventions_with_ratio):
                    break
            if remaining_budget < min(i["cost_inr"] for i in interventions_with_ratio):
                break

        # Risk chart data (bar by category)
        category_totals: Dict[str, float] = {}
        for a in allocated:
            cat = a["category"]
            category_totals[cat] = category_totals.get(cat, 0) + a["flood_risk_reduction_pct"]

        return {
            "total_budget_inr": total_budget,
            "budget_utilized_inr": total_budget - remaining_budget,
            "budget_remaining_inr": remaining_budget,
            "utilization_pct": round((total_budget - remaining_budget) / total_budget * 100, 1),
            "interventions": allocated,
            "total_readiness_gain": round(total_readiness_gain, 1),
            "total_risk_reduction_pct": round(min(total_risk_reduction, 85), 1),
            "wards_covered": len(set(a["ward_id"] for a in allocated)),
            "risk_reduction_by_category": [
                {"category": k, "risk_reduction_pct": round(v, 1)}
                for k, v in category_totals.items()
            ],
        }
