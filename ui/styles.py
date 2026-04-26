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

    /* THE BIG FIX: Force all inputs to have dark text and white backgrounds */
    QLineEdit, QComboBox, QSpinBox, QDateEdit {
        padding: 8px;
        border: 1px solid #cccccc;
        border-radius: 4px;
        background-color: white !important;
        color: #333333 !important; 
        selection-background-color: #004879;
    }

    /* Ensure the dropdown list inside the combo box is also styled */
    QComboBox QAbstractItemView {
        background-color: white;
        color: #333333;
        selection-background-color: #004879;
        selection-color: white;
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
    QPushButton#sidebarBtn:hover { background-color: #003a5c; }
"""