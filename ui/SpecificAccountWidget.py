from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QListWidget, QFrame, QPushButton)
from PyQt6.QtCore import Qt

from core.account.Account import Account
from core.transaction.TransactionRepository import TransactionRepository

from ui.AddTransactionDialog import AddTransactionDialog

class SpecificAccountWidget(QWidget):
    def __init__(self, account: Account):
        super().__init__()
        self.account = account
        self.repo = TransactionRepository("WealthTrackersDB.sqlite")
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # --- Middle Column: Analytics ---
        middle_layout = QVBoxLayout()
        middle_card = QFrame(objectName="card")
        m_card_layout = QVBoxLayout(middle_card)

        m_card_layout.addWidget(QLabel(f"{self.account.name} Overview", objectName="header"))

        # Placeholder for graphical analytics
        self.chart_placeholder = QLabel("Spending Analytics Graph Goes Here")
        self.chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        m_card_layout.addWidget(self.chart_placeholder, stretch=1)

        middle_layout.addWidget(middle_card)

        # --- Right Column: Balance & Transactions ---
        right_layout = QVBoxLayout()

        # Balance Card
        balance_card = QFrame(objectName="card")
        b_layout = QVBoxLayout(balance_card)
        b_layout.addWidget(QLabel("Current Balance", objectName="subtext"))
        self.balance_label = QLabel(f"${self.account.balance:,.2f}", objectName="header")
        b_layout.addWidget(self.balance_label)

        # Transaction Card
        tx_card = QFrame(objectName="card")
        tx_layout = QVBoxLayout(tx_card)
        tx_layout.addWidget(QLabel("Recent Activity", objectName="header"))

        self.tx_list = QListWidget()
        tx_layout.addWidget(self.tx_list)

        # Action Button
        self.add_tx_btn = QPushButton("+ Add Transaction")
        self.add_tx_btn.setObjectName("redButton")
        self.add_tx_btn.clicked.connect(self.trigger_add_transaction)
        tx_layout.addWidget(self.add_tx_btn)

        right_layout.addWidget(balance_card)
        right_layout.addWidget(tx_card, stretch=1)

        layout.addLayout(middle_layout, stretch=2)
        layout.addLayout(right_layout, stretch=1)

    def trigger_add_transaction(self):
        """Opens the dialog and saves the new transaction if accepted."""
        dialog = AddTransactionDialog(self.account.id, self)
        if dialog.exec():
            new_txn = dialog.new_txn
            if new_txn:
                self.repo.save_transaction(new_txn)
                # REMINDER to trigger a global refresh to update the sidebar balance, but for this page:
                self.refresh_data()

    def refresh_data(self):
        """Fetches transactions for this specific account from the DB."""
        self.tx_list.clear()

        # We fetch directly from the Repo to ensure we see the shared balance
        # impacts of linked Debit/Checking accounts
        transactions = self.repo.fetch_transactions(self.account.id)

        if not transactions:
            self.tx_list.addItem("No recent transactions found.")
        else:
            for tx in transactions:
                sign = "-" if tx.type == "EXPENSE" else "+"
                date_str = tx.date.strftime("%b %d")
                self.tx_list.addItem(f"{date_str}   {tx.vendor_name}   {sign}${tx.amount:,.2f}")

        # Update the balance label. Note: if you want the 'Shared' balance,
        # you may need to re-fetch the account from AccountRepository.
        self.balance_label.setText(f"${self.account.balance:,.2f}")