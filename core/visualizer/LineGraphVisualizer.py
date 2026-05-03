from matplotlib.figure import Figure
from typing import Dict
from core.visualizer.ChartFactory import ChartFactory

class LineGraphVisualizer(ChartFactory):
    def render(self, data_dict: Dict[str, float], title: str = "") -> Figure:
        # Matches the white background of the Dashboard/SpecificAccount cards
        fig = Figure(figsize=(6, 4), dpi=100, facecolor='white')
        ax = fig.add_subplot(111)

        if not data_dict:
            ax.text(0.5, 0.5, "No Historical Data", ha='center', va='center', color='#767676')
            ax.set_axis_off()
            return fig

        labels = list(data_dict.keys())
        values = list(data_dict.values())

        # Plot the primary line in Capital One Blue
        ax.plot(labels, values, color='#004a99', linewidth=2.5, marker='o',
                markersize=6, markerfacecolor='white', markeredgewidth=2)

        # Create a soft fill under the line for that professional "Area Chart" look
        ax.fill_between(labels, values, color='#004a99', alpha=0.1)

        # Styling to match the Bar graph visual
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#cccccc')
        ax.spines['bottom'].set_color('#cccccc')

        ax.set_title(title, fontsize=12, fontweight='bold', pad=15, color='#004a99')

        # Grid lines help tracking trends across the x-axis
        ax.yaxis.grid(True, linestyle='--', alpha=0.3)
        ax.xaxis.grid(False)
        ax.set_axisbelow(True)

        # Rotate x-labels if they are dates to prevent overlapping
        ax.tick_params(axis='x', rotation=30, labelsize=9, colors='#333333')
        ax.tick_params(axis='y', labelsize=9, colors='#333333')

        # Clean layout to ensure labels aren't cut off
        fig.tight_layout()

        return fig