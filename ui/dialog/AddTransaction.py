import uuid
import sqlite3
from decimal import Decimal
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt

from core.transaction.Transaction import Transaction

from ui.dialog.AddVendor import AddVendor
from ui.dialog.EditVendor import EditVendor


class AddTransaction(QDialog):
    def __init__(self, account_id, parent=None):
        super().__init__(parent)
        self.account_id = account_id
        self.new_txn = None
        self.setWindowTitle("Record Transaction")
        self.setFixedSize(400, 480)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Add Transaction", objectName="header", alignment=Qt.AlignmentFlag.AlignCenter))

        layout.addWidget(QLabel("Amount:"))
        self.amount_input = QLineEdit(placeholderText="0.00")
        layout.addWidget(self.amount_input)

        layout.addWidget(QLabel("Transaction Type:"))
        self.type_dropdown = QComboBox()
        self.type_dropdown.addItems(["EXPENSE", "INCOME", "TRANSFER_OUT", "TRANSFER_IN"])
        layout.addWidget(self.type_dropdown)

        # Vendor Selection Row
        layout.addWidget(QLabel("Vendor:"))
        vendor_row = QHBoxLayout()
        self.vendor_dropdown = QComboBox()
        self.load_vendors()
        self.vendor_dropdown.currentIndexChanged.connect(self.auto_select_category)
        vendor_row.addWidget(self.vendor_dropdown, stretch=1)

        # Add New Vendor
        add_v_btn = QPushButton("+")
        add_v_btn.setFixedWidth(35)
        add_v_btn.clicked.connect(self.open_add_vendor)
        vendor_row.addWidget(add_v_btn)

        # Edit Selected Vendor
        edit_v_btn = QPushButton("✎")
        edit_v_btn.setFixedWidth(35)
        edit_v_btn.clicked.connect(self.open_edit_vendor)
        vendor_row.addWidget(edit_v_btn)
        layout.addLayout(vendor_row)

        layout.addWidget(QLabel("Category:"))
        self.category_dropdown = QComboBox()
        self.load_categories()
        layout.addWidget(self.category_dropdown)

        layout.addStretch()
        save_btn = QPushButton("Save Transaction", objectName="redButton")
        save_btn.clicked.connect(self.handle_save)
        layout.addWidget(save_btn)

    def load_vendors(self):
        self.vendor_dropdown.clear()
        conn = sqlite3.connect("WealthTrackersDB.sqlite")

        for row in conn.execute("SELECT vendor_id, vendor_name FROM vendors ORDER BY vendor_name"):
            self.vendor_dropdown.addItem(row[1], row[0])

        conn.close()

    def load_categories(self):
        self.category_dropdown.clear()
        conn = sqlite3.connect("WealthTrackersDB.sqlite")

        for row in conn.execute("SELECT category_id, category_name FROM categories ORDER BY category_name"):
            self.category_dropdown.addItem(row[1], row[0])

        conn.close()

    def auto_select_category(self):
        v_id = self.vendor_dropdown.currentData()
        if not v_id: return

        conn = sqlite3.connect("WealthTrackersDB.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT default_category_id FROM vendors WHERE vendor_id = ?", (v_id,))
        row = cursor.fetchone()
        if row:
            idx = self.category_dropdown.findData(row[0])
            if idx >= 0: self.category_dropdown.setCurrentIndex(idx)

        conn.close()

    def open_add_vendor(self):
        if AddVendor(self).exec(): self.load_vendors()

    def open_edit_vendor(self):
        v_id = self.vendor_dropdown.currentData()

        if v_id and EditVendor(v_id, self).exec():
            self.load_vendors()
            self.auto_select_category()

    def handle_save(self):
        try:
            amt = Decimal(self.amount_input.text().strip())
            v_name = self.vendor_dropdown.currentText()
            v_id = self.vendor_dropdown.currentData()
            c_id = self.category_dropdown.currentData()
            t_type = self.type_dropdown.currentText()

            self.new_txn = Transaction(uuid.uuid4(), self.account_id, v_id, v_name,
                                       c_id, "", amt, datetime.now(), t_type)

            self.accept()
        except:
            QMessageBox.warning(self, "Error", "Invalid amount.")