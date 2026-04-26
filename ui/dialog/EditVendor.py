import sqlite3
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt

class EditVendor(QDialog):
    def __init__(self, vendor_id, parent=None):
        super().__init__(parent)
        self.vendor_id = vendor_id
        self.setWindowTitle("Edit Vendor Details")
        self.setFixedSize(350, 300)
        self.setup_ui()
        self.load_vendor_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        layout.addWidget(QLabel("Update Vendor", objectName="header", alignment=Qt.AlignmentFlag.AlignCenter))

        self.name_input = QLineEdit()
        layout.addWidget(QLabel("Vendor Name:"))
        layout.addWidget(self.name_input)

        self.category_dropdown = QComboBox()
        self.load_categories()
        layout.addWidget(QLabel("Default Category:"))
        layout.addWidget(self.category_dropdown)

        save_btn = QPushButton("Save Changes", objectName="redButton")
        save_btn.clicked.connect(self.handle_save)
        layout.addWidget(save_btn)

    def load_categories(self):
        conn = sqlite3.connect("WealthTrackersDB.sqlite")

        for row in conn.execute("SELECT category_id, category_name FROM categories ORDER BY category_name"):
            self.category_dropdown.addItem(row[1], row[0])

        conn.close()

    def load_vendor_data(self):
        conn = sqlite3.connect("WealthTrackersDB.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT vendor_name, default_category_id FROM vendors WHERE vendor_id = ?", (self.vendor_id,))
        row = cursor.fetchone()

        if row:
            self.name_input.setText(row[0])
            idx = self.category_dropdown.findData(row[1])
            if idx >= 0: self.category_dropdown.setCurrentIndex(idx)

        conn.close()

    def handle_save(self):
        name = self.name_input.text().strip()
        cat_id = self.category_dropdown.currentData()

        if not name: return

        conn = sqlite3.connect("WealthTrackersDB.sqlite")
        conn.execute("UPDATE vendors SET vendor_name = ?, default_category_id = ? WHERE vendor_id = ?",
                     (name, cat_id, self.vendor_id))
        conn.commit()
        conn.close()

        self.accept()