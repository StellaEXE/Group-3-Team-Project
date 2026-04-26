from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QFrame,
                             QLabel, QComboBox, QPushButton, QListWidget)

from ui.AnalyticsDialogue import AnalyticsDialog

from core.transaction.TransactionRepository import TransactionRepository
from core.auth.UserSession import UserSession

class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = TransactionRepository("WealthTrackersDB.sqlite")
        self.session = UserSession()
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # --- Middle Column: Analytics ---
        middle_layout = QVBoxLayout()
        middle_card = QFrame(objectName="card")
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

        # Totals Card
        totals_card = QFrame(objectName="card")
        t_layout = QVBoxLayout(totals_card)
        self.total_spending_label = QLabel("Total Spending: $0.00", objectName="header")
        self.total_income_label = QLabel("Total Money In: $0.00", objectName="subtext")
        t_layout.addWidget(self.total_spending_label)
        t_layout.addWidget(self.total_income_label)

        # Recent Activity Card
        recent_card = QFrame(objectName="card")
        r_layout = QVBoxLayout(recent_card)
        r_layout.addWidget(QLabel("Recent Activity (All Accounts)", objectName="header"))

        self.tx_list = QListWidget()
        r_layout.addWidget(self.tx_list)

        right_layout.addWidget(totals_card)
        right_layout.addWidget(recent_card, stretch=1)

        layout.addLayout(middle_layout, stretch=2)
        layout.addLayout(right_layout, stretch=1)

    def refresh_data(self):
        """Fetches transactions for all user accounts and updates the dashboard."""
        self.tx_list.clear()
        user_id = self.session.active_user_id
        if not user_id:
            self.tx_list.addItem("Please log in to view transactions.")
            return

        transactions = self.repo.fetch_user_transactions(user_id)

        total_spent = 0
        total_income = 0

        if not transactions:
            self.tx_list.addItem("No recent transactions found.")
        else:
            for tx in transactions:
                # Calculate totals
                if tx.type == "EXPENSE":
                    total_spent += tx.amount
                    sign = "-"
                else:
                    total_income += tx.amount
                    sign = "+"

                # Format list item
                date_str = tx.date.strftime("%b %d")
                self.tx_list.addItem(f"{date_str}   {tx.vendor_name}   {sign}${tx.amount:,.2f}")

        self.total_spending_label.setText(f"Total Spending: ${total_spent:,.2f}")
        self.total_income_label.setText(f"Total Money In: ${total_income:,.2f}")

    def show_detailed_analytics(self):
        dlg = AnalyticsDialog(self)
        dlg.exec()