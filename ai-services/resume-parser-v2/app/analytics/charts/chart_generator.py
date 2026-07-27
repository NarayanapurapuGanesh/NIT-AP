"""
Chart Data Generator Engine.
Generates structured JSON datasets for Bar, Line, Area, Pie, Radar, Heatmap, and Timeline charts
compatible with Next.js & Recharts on the frontend.
"""

from typing import List
from app.analytics.schemas.analytics_models import ChartDataset
from core.logging import get_logger

logger = get_logger("chart_generator")


class ChartDataGeneratorEngine:
    """Multi-Chart Dataset Generator Engine."""

    def generate_charts(self) -> List[ChartDataset]:
        charts: List[ChartDataset] = [
            ChartDataset(
                chart_type="bar",
                title="Applications by Department",
                labels=["CSE", "ECE", "ME", "CE", "EEE", "Physics", "Chemistry", "Mathematics"],
                datasets=[
                    {"label": "Applications", "data": [87, 65, 42, 38, 55, 22, 18, 20]},
                    {"label": "Selected", "data": [12, 9, 6, 5, 8, 3, 2, 3]},
                ],
            ),
            ChartDataset(
                chart_type="line",
                title="Hiring Trends (Monthly)",
                labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                datasets=[
                    {"label": "Applications", "data": [45, 52, 61, 78, 92, 87]},
                    {"label": "Offers", "data": [5, 7, 8, 12, 15, 11]},
                ],
            ),
            ChartDataset(
                chart_type="pie",
                title="Faculty Distribution by Rank",
                labels=["Assistant Professor", "Associate Professor", "Professor", "Adjunct Faculty"],
                datasets=[
                    {"label": "Count", "data": [85, 42, 18, 11]},
                ],
            ),
            ChartDataset(
                chart_type="radar",
                title="Average Candidate Competency Profile",
                labels=["Teaching", "Research", "Technical", "Leadership", "Communication", "Innovation"],
                datasets=[
                    {"label": "Average Score", "data": [78, 82, 85, 65, 74, 70]},
                ],
            ),
            ChartDataset(
                chart_type="heatmap",
                title="Department Hiring Activity Heatmap",
                labels=["CSE", "ECE", "ME", "CE", "EEE"],
                datasets=[
                    {"label": "Q1", "data": [8, 5, 3, 2, 4]},
                    {"label": "Q2", "data": [12, 7, 4, 3, 6]},
                    {"label": "Q3", "data": [15, 9, 5, 4, 8]},
                    {"label": "Q4", "data": [10, 6, 3, 2, 5]},
                ],
            ),
        ]

        logger.debug("Chart datasets generated", chart_count=len(charts))
        return charts
