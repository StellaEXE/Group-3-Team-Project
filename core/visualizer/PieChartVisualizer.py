import matplotlib.pyplot as plt

from matplotlib.figure import Figure
from typing import Dict

from core.visualizer.ChartFactory import ChartFactory

class PieChartVisualizer(ChartFactory):
    def render(self, data_dict: Dict[str, Dict[str, float]], title: str = "") -> Figure:
        fig = Figure(figsize=(5, 5), dpi=100, facecolor='white')
        ax = fig.add_subplot(111)

        if not data_dict:
            ax.text(0.5, 0.5, "No Data", ha='center', va='center', color='#767676')
            ax.set_axis_off()
            return fig

        total_income = sum(p.get('Income', 0) for p in data_dict.values())
        total_expense = sum(p.get('Expense', 0) for p in data_dict.values())
        total_bal = sum(max(0, p.get('Total Balance', 0)) for p in data_dict.values())

        labels_raw = ['Income', 'Expense', 'Total Balance']
        values_raw = [total_income, total_expense, total_bal]

        labels = [l for l, v in zip(labels_raw, values_raw) if v > 0]
        values = [v for v in values_raw if v > 0]

        if not values:
            ax.text(0.5, 0.5, "No positive assets", ha='center', va='center', color='#767676')
            ax.set_axis_off()
            return fig

        color_map = {'Income': '#004a99', 'Expense': '#D22E1E', 'Total Balance': '#00d2ff'}
        colors = [color_map[l] for l in labels]

        wedges, texts, autotexts = ax.pie(
            values, labels=labels, autopct='%1.0f%%', startangle=90, colors=colors,
            pctdistance=0.85, wedgeprops={'width': 0.3, 'edgecolor': 'white'}
        )

        plt.setp(autotexts, size=9, weight="bold", color="white")
        ax.set_title(title, fontsize=12, fontweight='bold', pad=15, color='#004879')
        fig.tight_layout()
        return fig