from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QFrame,
                             QLabel, QComboBox, QPushButton)

from ui.dialog.Analytics import Analytics
from ui.component.TransactionList import TransactionList

from core.transaction.TransactionRepository import TransactionRepository
from core.auth.UserSession import UserSession
from core.utils.Signal import global_signal

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = TransactionRepository("WealthTrackersDB.sqlite")
        self.session = UserSession()

        self.setup_ui()
        self.refresh_data()

        # Respond to global updates
        global_signal.refresh_requested.connect(self.refresh_data)

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

        # Placeholder for the future graph integration
        self.chart_placeholder = QLabel("Transaction data visualization goes here")
        self.chart_placeholder.setObjectName("subtext")
        self.chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.chart_placeholder, stretch=1)

        details_btn = QPushButton("View Spending Details")
        # details_btn.clicked.connect(self.show_detailed_analytics)
        card_layout.addWidget(details_btn)

        middle_layout.addWidget(middle_card)

        # --- Right Column: Transactions & Totals ---
        right_layout = QVBoxLayout()

        # Totals Summary Card
        totals_card = QFrame(objectName="card")
        t_layout = QVBoxLayout(totals_card)
        self.total_spending_label = QLabel("Total Spending: $0.00", objectName="header")
        self.total_income_label = QLabel("Total Money In: $0.00", objectName="subtext")
        t_layout.addWidget(self.total_spending_label)
        t_layout.addWidget(self.total_income_label)

        # Recent Activity Card
        recent_card = QFrame(objectName="card")
        r_layout = QVBoxLayout(recent_card)
        r_layout.addWidget(QLabel("Recent Activity (Global)", objectName="header"))

        # Using the new reusable component
        self.tx_list = TransactionList()
        r_layout.addWidget(self.tx_list)

        right_layout.addWidget(totals_card)
        right_layout.addWidget(recent_card, stretch=1)

        layout.addLayout(middle_layout, stretch=2)
        layout.addLayout(right_layout, stretch=1)

    def refresh_data(self):
        """Calculates global totals and refreshes the transaction component."""
        # GUARD: Avoid login crashes
        user_id = self.session.active_user_id
        if not user_id:
            return

        transactions = self.repo.fetch_user_transactions(user_id)

        total_spent = 0
        total_income = 0

        for tx in transactions:
            if tx.type in ("EXPENSE", "TRANSFER_OUT"):
                total_spent += tx.amount
            elif tx.type in ("INCOME", "TRANSFER_IN"):
                total_income += tx.amount

        # Update labels
        self.total_spending_label.setText(f"Total Spending: ${total_spent:,.2f}")
        self.total_income_label.setText(f"Total Money In: ${total_income:,.2f}")

        # Refresh the reusable transaction list component
        self.tx_list.update_with_data(transactions)