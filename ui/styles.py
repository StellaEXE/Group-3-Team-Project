"""
This entire thing is just a disgusting piece of crap that should never ever
have existed. UI designing LOOOOVEEES QSS/CSS styles which just pisses me off
as this stuff NEVER is useful to learn. It's not real programming and all it
does is trying to larp as someone doing something useful when AI can just handle
all of this with little to no issue. Without AI I would never touch this part
of programming/project design EVER since it is just a massive waste of time.
"""

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

    /* THE BIG FIX: Force all inputs and the list sidebar to white background */
    QLineEdit, QComboBox, QSpinBox, QDateEdit, QListWidget, QListWidget::viewport {
        background-color: white !important;
        color: #333333 !important; 
        border: 1px solid #cccccc;
        border-radius: 4px;
        padding: 8px;
    }

    QListWidget {
        border: none; /* Keep the sidebar list clean */
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

    /* Action Buttons (like the + or ... buttons) */
    QPushButton#actionButton {
        background-color: #e0e0e0;
        color: #333333;
        font-weight: bold;
        padding: 8px 12px;
        border-radius: 4px;
    }
    QPushButton#actionButton:hover {
        background-color: #cccccc;
    }
    
    /* Table Styling */
    QTableWidget {
        background-color: white;
        color: #333333; /* Fixed: Forced text to be black */
        border: 1px solid #cccccc;
        border-radius: 4px;
        gridline-color: #e0e0e0;
        selection-background-color: #004879;
        selection-color: white;
        alternate-background-color: #f9f9f9;
    }
    
    QHeaderView::section {
        background-color: #F4F5F7;
        color: #004879;
        font-weight: bold;
        padding: 5px;
        border: none;
        border-bottom: 2px solid #004879;
    }
"""