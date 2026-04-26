from abc import ABC, abstractmethod
from typing import Dict
from matplotlib.figure import Figure

class ChartFactory(ABC):
    """Abstract base class for all chart visualizers"""

    @abstractmethod
    def render(self, data_dict: Dict[str, float], title: str = "") -> Figure:
        """Processes data and returns a styled Matplotlib Figure"""
        pass