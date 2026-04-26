from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QStackedWidget, QFrame, QMessageBox)
from PyQt6.QtCore import Qt

from ui.AddAccountDialog import AddAccountDialog
from ui.DashboardWidget import DashboardWidget
from ui.SpecificAccountWidget import SpecificAccountWidget
from core.account.AccountRepository import AccountRepository
from core.auth.UserSession import UserSession


class MainAppWidget(QWidget):
    def __init__(self, on_logout):
        super().__init__()
        self.on_logout = on_logout
        self.session = UserSession()
        self.repo = AccountRepository("WealthTrackersDB.sqlite")
        self.active_account_pages = {}  # Map index to account_id

        self.setup_ui()
        self.load_user_accounts()

    def setup_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # --- Sidebar ---
        self.sidebar = QFrame(objectName="sidebar")
        self.sidebar.setFixedWidth(250)
        self.sidebar_layout = QVBoxLayout(self.sidebar)

        logo = QLabel("WealthTrackers")
        logo.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin: 20px 10px;")
        self.sidebar_layout.addWidget(logo)

        self.dash_btn = QPushButton("Dashboard", objectName="sidebarBtn")
        self.sidebar_layout.addWidget(self.dash_btn)

        self.sidebar_layout.addWidget(
            QLabel("ACCOUNTS", styleSheet="color: #88aacc; font-size: 11px; margin-top: 15px; padding-left: 10px;"))

        self.accounts_layout = QVBoxLayout()
        self.sidebar_layout.addLayout(self.accounts_layout)

        self.add_acc_btn = QPushButton("+ Add Account", objectName="sidebarBtn")
        self.add_acc_btn.clicked.connect(self.trigger_add_account)
        self.sidebar_layout.addWidget(self.add_acc_btn)

        self.sidebar_layout.addStretch()

        # Action Buttons
        self.delete_btn = QPushButton("🗑 Delete Account", objectName="sidebarBtn")
        self.delete_btn.clicked.connect(self.trigger_delete_account)
        self.sidebar_layout.addWidget(self.delete_btn)

        self.logout_btn = QPushButton("🚪 Logout", objectName="sidebarBtn")
        self.logout_btn.clicked.connect(self.trigger_logout)
        self.sidebar_layout.addWidget(self.logout_btn)

        # --- Content ---
        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(DashboardWidget())
        self.dash_btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))

        self.layout.addWidget(self.sidebar)
        self.layout.addWidget(self.content_stack, stretch=1)

    def load_user_accounts(self):
        if not self.session.active_user_id: return
        accounts = self.repo.fetch_all_accounts(self.session.active_user_id)

        for acc in accounts:
            try:
                dec = acc.get_decrypted_number(self.session.get_key())
                display = f"{acc.name} (...{dec[-4:]})"
            except:
                display = acc.name

            btn = QPushButton(display, objectName="sidebarBtn")
            self.accounts_layout.addWidget(btn)

            page = SpecificAccountWidget(acc)
            self.content_stack.addWidget(page)
            idx = self.content_stack.count() - 1
            self.active_account_pages[idx] = acc.id

            btn.clicked.connect(lambda checked, i=idx: self.content_stack.setCurrentIndex(i))

    def trigger_delete_account(self):
        current_idx = self.content_stack.currentIndex()

        if current_idx == 0:
            QMessageBox.information(self, "Action Required", "Please select an account from the sidebar first.")
            return

        acc_id = self.active_account_pages.get(current_idx)
        reply = QMessageBox.warning(self, 'Confirm Deletion',
                                    "Are you sure? This will wipe ALL transactions for this account.",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            if self.repo.delete_financial_account(acc_id):
                self.refresh_ui()
                self.content_stack.setCurrentIndex(0)

    def trigger_add_account(self):
        if AddAccountDialog(self).exec():
            self.refresh_ui()

    def refresh_ui(self):
        while self.accounts_layout.count():
            item = self.accounts_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        while self.content_stack.count() > 1:
            w = self.content_stack.widget(1)
            self.content_stack.removeWidget(w)
            w.deleteLater()

        self.active_account_pages = {}
        self.load_user_accounts()

    def trigger_logout(self):
        if QMessageBox.question(self, 'Logout', 'Confirm logout?') == QMessageBox.StandardButton.Yes:
            self.on_logout()