import sys

from PyQt6.QtWidgets import QApplication
from ui.MainWindow import MainWindow
from ui.styles import CAPITAL_ONE_STYLE

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # APPLY GLOBAL THEME
    app.setStyleSheet(CAPITAL_ONE_STYLE)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())