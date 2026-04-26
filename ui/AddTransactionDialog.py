import uuid
from decimal import Decimal
from datetime import datetime
import sqlite3
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt
from core.transaction.Transaction import Transaction

class AddTransactionDialog(QDialog):
    def __init__(self, account_id, parent=None):
        super().__init__(parent)
        self.account_id = account_id
        self.setWindowTitle("Add Transaction")
        self.setFixedSize(350, 450)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        layout.addWidget(QLabel("New Transaction", objectName="header", alignment=Qt.AlignmentFlag.AlignCenter))

        self.amount_input = QLineEdit(placeholderText="Amount (e.g., 24.50)")
        layout.addWidget(self.amount_input)

        # Type Selection
        layout.addWidget(QLabel("Type:"))
        self.type_dropdown = QComboBox()
        self.type_dropdown.addItems(["EXPENSE", "INCOME"])
        layout.addWidget(self.type_dropdown)

        # Vendor Selection (Fetched from DB)
        layout.addWidget(QLabel("Vendor:"))
        self.vendor_dropdown = QComboBox()
        self.load_vendors()
        layout.addWidget(self.vendor_dropdown)

        # Category Selection (Fetched from DB)
        layout.addWidget(QLabel("Category:"))
        self.category_dropdown = QComboBox()
        self.load_categories()
        layout.addWidget(self.category_dropdown)

        save_btn = QPushButton("Save Transaction", objectName="redButton")
        save_btn.clicked.connect(self.handle_save)
        layout.addWidget(save_btn)

    def load_vendors(self):
        conn = sqlite3.connect("WealthTrackersDB.sqlite")
        for row in conn.execute("SELECT vendor_id, vendor_name FROM vendors ORDER BY vendor_name"):
            self.vendor_dropdown.addItem(row[1], row[0])
        conn.close()

    def load_categories(self):
        conn = sqlite3.connect("WealthTrackersDB.sqlite")
        for row in conn.execute("SELECT category_id, category_name FROM categories ORDER BY category_name"):
            self.category_dropdown.addItem(row[1], row[0])
        conn.close()

    def handle_save(self):
        try:
            amt = Decimal(self.amount_input.text())
            v_id = self.vendor_dropdown.currentData()
            c_id = self.category_dropdown.currentData()
            t_type = self.type_dropdown.currentText()

            self.new_txn = Transaction(
                uuid.uuid4(), self.account_id, v_id, "", c_id, "",
                amt, datetime.now(), t_type
            )
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", "Invalid amount format.")