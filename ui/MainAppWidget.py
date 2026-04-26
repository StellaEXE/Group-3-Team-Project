from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QStackedWidget, QFrame, QMessageBox)

from ui.AddAccountDialog import AddAccountDialog
from ui.DashboardWidget import DashboardWidget
from ui.SpecificAccountWidget import SpecificAccountWidget

from core.account.AccountRepository import AccountRepository
from core.auth.UserSession import UserSession

class MainAppWidget(QWidget):
    def __init__(self, on_logout):
        super().__init__()
        self.on_logout = on_logout

        # Backend initialization
        self.session = UserSession()
        self.repo = AccountRepository("WealthTrackersDB.sqlite")

        self.setup_ui()
        self.load_user_accounts()

    def setup_ui(self):
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # --- Left Sidebar ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(250)
        self.sidebar_layout = QVBoxLayout(self.sidebar)

        logo_label = QLabel("WealthTrackers")
        logo_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin: 20px 10px;")
        self.sidebar_layout.addWidget(logo_label)

        self.dash_btn = QPushButton("Dashboard")
        self.dash_btn.setObjectName("sidebarBtn")
        self.sidebar_layout.addWidget(self.dash_btn)

        self.sidebar_layout.addWidget(
            QLabel("ACCOUNTS", styleSheet="color: #88aacc; font-size: 12px; margin-top: 20px; padding-left: 10px;"))

        # Populate this layout with DB data in load_user_accounts()
        self.accounts_layout = QVBoxLayout()
        self.accounts_layout.setSpacing(0)
        self.accounts_layout.setContentsMargins(0,0,0,0)
        self.sidebar_layout.addLayout(self.accounts_layout)

        self.add_acc_btn = QPushButton("+ Add Account")
        self.add_acc_btn.setObjectName("sidebarBtn")
        self.add_acc_btn.clicked.connect(self.trigger_add_account)
        self.sidebar_layout.addWidget(self.add_acc_btn)

        self.sidebar_layout.addStretch()

        settings_btn = QPushButton("⚙ Settings (Logout)")
        settings_btn.setObjectName("sidebarBtn")
        settings_btn.clicked.connect(self.trigger_logout)
        self.sidebar_layout.addWidget(settings_btn)

        # --- Central Content Area ---
        self.content_stack = QStackedWidget()
        self.dashboard_view = DashboardWidget()
        self.content_stack.addWidget(self.dashboard_view)
        self.dash_btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))

        self.layout.addWidget(self.sidebar)
        self.layout.addWidget(self.content_stack, stretch=1)
        self.setLayout(self.layout)

    def load_user_accounts(self):
        """Fetches from SQLite and builds UI dynamically"""
        if not self.session.active_user_id:
            return

        accounts = self.repo.fetch_all_accounts(self.session.active_user_id)

        # For each account found in the DB...
        for account in accounts:
            # Safely decrypt the last 4 digits using the session key
            try:
                decrypted_num = account.get_decrypted_number(self.session.get_key())
                display_num = decrypted_num[-4:] if len(decrypted_num) >= 4 else "****"
            except Exception:
                display_num = "ERROR"

            # Create the sidebar button
            btn_text = f"{account.name} (...{display_num})"
            btn = QPushButton(btn_text)
            btn.setObjectName("sidebarBtn")
            self.accounts_layout.addWidget(btn)

            # Create the specific UI page for this account
            account_view = SpecificAccountWidget(account)
            self.content_stack.addWidget(account_view)

            # Index logic: Dashboard is 0, first account is 1, second is 2...
            page_index = self.content_stack.count() - 1

            btn.clicked.connect(lambda checked, idx=page_index: self.content_stack.setCurrentIndex(idx))

    def trigger_add_account(self):
        dialog = AddAccountDialog(self)
        if dialog.exec():
            account_to_save = dialog.new_account

            if account_to_save and self.session.active_user_id:
                self.repo.save_new_account(self.session.active_user_id, account_to_save)
                self.refresh_ui()

    def refresh_ui(self):
        """Clears the sidebar and stacks safely, then re-fetches from DB"""
        # Safely remove existing buttons from layout and delete the widgets
        while self.accounts_layout.count():
            item = self.accounts_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Clear the stacked widget pages (keep the dashboard at index 0)
        while self.content_stack.count() > 1:
            widget = self.content_stack.widget(1)
            self.content_stack.removeWidget(widget)
            widget.deleteLater()

        # Re-fetch and re-build
        self.load_user_accounts()

    def trigger_logout(self):
        reply = QMessageBox.question(self, 'Log Out',
                                     'Are you sure you want to log out?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.on_logout()