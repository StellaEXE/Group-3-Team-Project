import sqlite3
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFrame, QLabel, QLineEdit, QPushButton, QMessageBox)

from core.auth.AuthenticationService import AuthenticationService
from core.auth.UserSession import UserSession

class Login(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.auth_service = AuthenticationService()
        self.session = UserSession()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        login_box = QFrame(objectName="card")
        login_box.setFixedSize(400, 400)
        box_layout = QVBoxLayout(login_box)
        box_layout.setContentsMargins(40, 40, 40, 40)
        box_layout.setSpacing(15)

        box_layout.addWidget(QLabel("Sign In", objectName="header", alignment=Qt.AlignmentFlag.AlignCenter))

        self.username_input = QLineEdit(placeholderText="Username")
        self.password_input = QLineEdit(placeholderText="Password", echoMode=QLineEdit.EchoMode.Password)

        login_btn = QPushButton("Sign In", objectName="redButton")
        login_btn.clicked.connect(self.handle_login)

        box_layout.addWidget(self.username_input)
        box_layout.addWidget(self.password_input)
        box_layout.addWidget(login_btn)
        layout.addWidget(login_box)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            conn = sqlite3.connect("WealthTrackersDB.sqlite")
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, password_hash, encryption_salt FROM users WHERE username = ?", (username,))
            user_data = cursor.fetchone()
            conn.close()

            if user_data:
                user_id, stored_hash, salt = user_data

                if self.auth_service.verify_password(password, stored_hash):
                    # Derive key and start real session
                    aes_key = AuthenticationService.derive_aes_key(password, salt)
                    self.session.start_session(user_id, aes_key)
                    self.on_login_success()

                    return

            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Database error: {e}")