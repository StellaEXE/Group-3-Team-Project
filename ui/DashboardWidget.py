from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout,
                             QFrame, QLabel, QComboBox, QPushButton, QListWidget)

from ui.AnalyticsDialogue import AnalyticsDialog

class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()

        # --- Middle Column: Analytics ---
        middle_layout = QVBoxLayout()
        middle_card = QFrame()
        middle_card.setObjectName("card")
        card_layout = QVBoxLayout(middle_card)

        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Analytics Overview", objectName="header"))

        self.chart_dropdown = QComboBox()
        self.chart_dropdown.addItems(["Pie Chart", "Bar Graph", "Line Chart"])
        header_layout.addWidget(self.chart_dropdown, alignment=Qt.AlignmentFlag.AlignRight)

        card_layout.addLayout(header_layout)

        self.chart_placeholder = QLabel("Add an account to start")
        self.chart_placeholder.setObjectName("subtext")
        self.chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.chart_placeholder, stretch=1)

        details_btn = QPushButton("View Spending Details")
        details_btn.clicked.connect(self.show_detailed_analytics)
        card_layout.addWidget(details_btn)

        middle_layout.addWidget(middle_card)

        # --- Right Column: Transactions & Totals ---
        right_layout = QVBoxLayout()

        totals_card = QFrame()
        totals_card.setObjectName("card")
        t_layout = QVBoxLayout(totals_card)
        t_layout.addWidget(QLabel("Total Spending: $0.00", objectName="header"))
        t_layout.addWidget(QLabel("Total Money In: $0.00", objectName="subtext"))

        recent_card = QFrame()
        recent_card.setObjectName("card")
        r_layout = QVBoxLayout(recent_card)
        r_layout.addWidget(QLabel("Recent Transactions", objectName="header"))
        self.tx_list = QListWidget()
        self.tx_list.addItem("Add an account to start")
        r_layout.addWidget(self.tx_list)

        right_layout.addWidget(totals_card)
        right_layout.addWidget(recent_card, stretch=1)

        layout.addLayout(middle_layout, stretch=2)
        layout.addLayout(right_layout, stretch=1)
        self.setLayout(layout)

    def show_detailed_analytics(self):
        dlg = AnalyticsDialog(self)
        dlg.exec()