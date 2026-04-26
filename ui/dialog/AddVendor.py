import sqlite3
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QComboBox, QMessageBox, QHBoxLayout)
from PyQt6.QtCore import Qt

class AddVendor(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Vendor")
        self.setFixedSize(350, 250)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        layout.addWidget(QLabel("Register New Vendor", objectName="header", alignment=Qt.AlignmentFlag.AlignCenter))

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Vendor Name (e.g., Starbucks)")
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Default Category:"))
        self.category_dropdown = QComboBox()
        self.load_categories()
        layout.addWidget(self.category_dropdown)

        save_btn = QPushButton("Add Vendor", objectName="redButton")
        save_btn.clicked.connect(self.handle_save)
        layout.addWidget(save_btn)

    def load_categories(self):
        conn = sqlite3.connect("WealthTrackersDB.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT category_id, category_name FROM categories ORDER BY category_name")

        for row in cursor.fetchall():
            self.category_dropdown.addItem(row[1], row[0])

        conn.close()

    def handle_save(self):
        name = self.name_input.text().strip()
        cat_id = self.category_dropdown.currentData()

        if not name:
            QMessageBox.warning(self, "Error", "Vendor name is required.")
            return

        try:
            conn = sqlite3.connect("WealthTrackersDB.sqlite")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO vendors (vendor_name, default_category_id) VALUES (?, ?)", (name, cat_id))
            conn.commit()
            conn.close()
            self.accept()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "This vendor already exists.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Database error: {e}")