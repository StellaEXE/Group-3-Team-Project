from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from typing import Dict
from .ChartFactory import ChartFactory


class PieChartVisualizer(ChartFactory):
    def render(self, data_dict: Dict[str, float], title: str = "") -> Figure:
        # Use a white background
        fig = Figure(figsize=(5, 5), dpi=100, facecolor='white')
        ax = fig.add_subplot(111)

        if not data_dict:
            ax.text(0.5, 0.5, "No Spending Data", ha='center', va='center')
            return fig

        labels = list(data_dict.keys())
        values = list(data_dict.values())

        # Capital One color palette
        colors = ['#004a99', '#00d2ff', '#002d5c', '#767676', '#a5a5a5']

        # Create the pie chart
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct='%1.0f%%',
            startangle=90,
            colors=colors,
            pctdistance=0.85,  # Move percentages toward the edge
            wedgeprops={'width': 0.3, 'edgecolor': 'white'}  # THE DONUT HOLE
        )

        # Style the percentage text
        plt.setp(autotexts, size=9, weight="bold", color="white")
        plt.setp(texts, size=10)

        ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
        fig.tight_layout()
        return fig