from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QListWidget, QFrame)
from PyQt6.QtCore import Qt

from core.account.Account import Account

class SpecificAccountWidget(QWidget):
    def __init__(self, account: Account):
        super().__init__()
        self.account = account
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # --- Middle Column: Analytics ---
        middle_layout = QVBoxLayout()
        middle_card = QFrame(objectName="card")
        m_card_layout = QVBoxLayout(middle_card)

        m_card_layout.addWidget(QLabel(f"{self.account.name} Overview", objectName="header"))
        self.chart_placeholder = QLabel("Spending Analytics Graph Goes Here")
        self.chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        m_card_layout.addWidget(self.chart_placeholder, stretch=1)

        middle_layout.addWidget(middle_card)

        # --- Right Column: Balance & Transactions ---
        right_layout = QVBoxLayout()

        balance_card = QFrame(objectName="card")
        b_layout = QVBoxLayout(balance_card)
        b_layout.addWidget(QLabel("Current Balance", objectName="subtext"))
        self.balance_label = QLabel(f"${self.account.balance:,.2f}", objectName="header")
        b_layout.addWidget(self.balance_label)

        tx_card = QFrame(objectName="card")
        tx_layout = QVBoxLayout(tx_card)
        tx_layout.addWidget(QLabel("Recent Activity", objectName="header"))
        self.tx_list = QListWidget()
        tx_layout.addWidget(self.tx_list)

        right_layout.addWidget(balance_card)
        right_layout.addWidget(tx_card, stretch=1)

        layout.addLayout(middle_layout, stretch=2)
        layout.addLayout(right_layout, stretch=1)
        self.setLayout(layout)

    def refresh_data(self):
        self.tx_list.clear()
        transactions = self.account.get_transactions()

        if not transactions:
            self.tx_list.addItem("No recent transactions found.")
            return

        for tx in transactions:
            # Assumes transaction object has .vendor_name, .amount, and .transaction_date
            date_str = tx.transaction_date.strftime("%b %d")
            self.tx_list.addItem(f"{date_str}   {tx.vendor_name}   -${tx.amount:,.2f}")