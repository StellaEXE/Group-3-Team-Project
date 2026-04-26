from PyQt6.QtWidgets import QMainWindow, QStackedWidget

from ui.LoginWidget import LoginWidget
from ui.MainAppWidget import MainAppWidget
from ui.styles import CAPITAL_ONE_STYLE

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WealthTrackers")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(CAPITAL_ONE_STYLE)

        self.main_stack = QStackedWidget()
        self.setCentralWidget(self.main_stack)

        self.login_view = LoginWidget(self.show_main_app)
        self.main_stack.addWidget(self.login_view)

    def show_main_app(self):
        self.app_view = MainAppWidget(self.show_login)
        self.main_stack.addWidget(self.app_view)
        self.main_stack.setCurrentWidget(self.app_view)

    def show_login(self):
        self.main_stack.setCurrentWidget(self.login_view)