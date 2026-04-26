CAPITAL_ONE_STYLE = """
    /* Global Backgrounds */
    QMainWindow, QDialog, QMessageBox, QStackedWidget, QWidget#central {
        background-color: #F4F5F7;
    }

    /* Cards and Containers */
    QFrame#card {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }

    QFrame#sidebar {
        background-color: #004879;
    }

    /* Text Elements */
    QLabel, QMessageBox QLabel {
        font-family: 'Segoe UI', Arial, sans-serif;
        color: #333333;
    }
    QLabel#header {
        font-size: 22px;
        font-weight: bold;
        color: #004879;
    }
    QLabel#subtext {
        color: #666666;
        font-size: 13px;
    }

    /* FORCED LIGHT THEME FOR LISTS (Recent Activity) */
    QListWidget {
        background-color: white;
        color: #333333;
        border: none;
        outline: none;
        font-size: 14px;
    }
    QListWidget::item {
        background-color: white;
        color: #333333;
        padding: 12px;
        border-bottom: 1px solid #f0f0f0;
    }
    QListWidget::item:selected {
        background-color: #e6f2ff;
        color: #004879;
        border-left: 4px solid #D22E1E;
    }

    /* INPUT BOXES (Login / Add Account Fix) */
    QLineEdit {
        padding: 10px;
        border: 1px solid #cccccc;
        border-radius: 4px;
        background-color: white;
        color: #333333; /* Dark text */
        font-size: 14px;
    }
    QLineEdit:focus {
        border: 1px solid #004879;
    }

    /* Dropdown / Combo Styling */
    QComboBox {
        padding: 10px;
        border: 1px solid #cccccc;
        border-radius: 4px;
        background-color: white;
        color: #333333;
    }

    /* Buttons */
    QPushButton {
        background-color: #004879;
        color: white;
        border: none;
        padding: 10px 18px;
        border-radius: 4px;
        font-weight: bold;
    }
    QPushButton:hover { background-color: #003a5c; }

    QPushButton#redButton { background-color: #D22E1E; }
    QPushButton#redButton:hover { background-color: #b02619; }

    QPushButton#sidebarBtn {
        background-color: transparent;
        color: white;
        text-align: left;
        padding: 12px;
    }
    QPushButton#sidebarBtn:hover {
        background-color: #003a5c;
    }
"""