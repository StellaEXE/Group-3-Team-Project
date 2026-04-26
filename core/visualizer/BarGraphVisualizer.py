from matplotlib.figure import Figure
from typing import Dict

from core.visualizer.ChartFactory import ChartFactory

class BarGraphVisualizer(ChartFactory):
    def render(self, data_dict: Dict[str, float], title: str = "") -> Figure:
        # Use a white background
        fig = Figure(figsize=(6, 4), dpi=100, facecolor='white')
        ax = fig.add_subplot(111)

        if not data_dict:
            ax.text(0.5, 0.5, "No Data", ha='center', va='center')
            return fig

        labels = list(data_dict.keys())
        values = list(data_dict.values())

        bars = ax.bar(labels, values, color='#004a99', alpha=0.8)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        ax.set_title(title, fontsize=12, fontweight='bold', pad=15)
        ax.tick_params(axis='x', rotation=30, labelsize=9)

        # Add grid lines for readability
        ax.yaxis.grid(True, linestyle='--', alpha=0.3)
        ax.set_axisbelow(True)  # Ensure grid is behind the bars

        # Add dollar labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'${height:,.0f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 5),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=8, fontweight='bold', color='#444444')

        fig.tight_layout()

        return fig