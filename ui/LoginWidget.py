from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFrame,
                             QLabel, QLineEdit, QPushButton)

class LoginWidget(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        login_box = QFrame()
        login_box.setObjectName("card")
        login_box.setFixedSize(400, 350)
        box_layout = QVBoxLayout(login_box)
        box_layout.setContentsMargins(40, 40, 40, 40)
        box_layout.setSpacing(15)

        title = QLabel("Sign In")
        title.setObjectName("header")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        login_btn = QPushButton("Sign In")
        login_btn.setObjectName("redButton")
        login_btn.clicked.connect(self.handle_login)

        box_layout.addWidget(title)
        box_layout.addWidget(self.username_input)
        box_layout.addWidget(self.password_input)
        box_layout.addWidget(login_btn)

        layout.addWidget(login_box)
        self.setLayout(layout)

    def handle_login(self):
        # Insert AuthenticationService logic here
        self.on_login_success()
