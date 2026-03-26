# src/main.py
import sys
from PyQt6.QtWidgets import QApplication

from src.UI.login_window import LoginWindow
from src.UI.main_window import MainWindow
from src.db import StorageModule
from src.utils.settings import get_stay_connected

GLOBAL_QSS = """
/* Global Font & Background */
QWidget {
    font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
    font-size: 14px;
    background-color: #0d1117;
    color: #c9d1d9;
}

/* Frames & Cards */
QFrame {
    border: none;
}

/* Push Buttons */
QPushButton {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 16px;
    outline: none;
}
QPushButton:hover {
    background-color: #30363d;
    border-color: #8b949e;
}
QPushButton:pressed {
    background-color: #282e33;
}

/* Line Edits & Inputs */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #010409;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 12px;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #a3e635;
    background-color: #0d1117;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #0d1117;
    width: 10px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #30363d;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #484f58;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

QScrollBar:horizontal {
    border: none;
    background: #0d1117;
    height: 10px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:horizontal {
    background: #30363d;
    min-width: 20px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal:hover {
    background: #484f58;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
}

/* Table Widget */
QTableWidget {
    background-color: #0d1117;
    alternate-background-color: #161b22;
    gridline-color: #30363d;
    border: 1px solid #30363d;
    border-radius: 6px;
}
QHeaderView::section {
    background-color: #161b22;
    color: #8b949e;
    padding: 6px;
    border: none;
    border-bottom: 1px solid #30363d;
    font-weight: bold;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #30363d;
    background: #161b22;
    border-radius: 6px;
}
QTabBar::tab {
    background: #0d1117;
    color: #8b949e;
    padding: 8px 20px;
    border: 1px solid transparent;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:selected {
    color: #a3e635;
    border-bottom: 2px solid #a3e635;
}
QTabBar::tab:hover:!selected {
    color: #c9d1d9;
    background: #161b22;
}
"""


# src/main.py


def main():
    app = QApplication(sys.argv)

    def start_main_window(company_data):
        main_win = MainWindow(company_data)
        # Change to maximized or full screen here
        main_win.showMaximized()
        app.main_window = main_win

    # Check if we have saved credentials
    stay, email, password = get_stay_connected()
    if stay and email and password:
        storage = StorageModule()
        if storage.connecter_entreprise(email, password):
            with storage._connect() as conn:
                row = conn.execute("SELECT nom, secteur, email, devise FROM entreprise_account WHERE email = ?", (email,)).fetchone()
                if row:
                    company_data = dict(row)
                    start_main_window(company_data)
                else:
                    login = LoginWindow(start_main_window)
                    # Change to maximized or full screen here
                    login.showMaximized()
        else:
            # Credentials invalid, clear them
            from src.utils.settings import clear_stay_connected
            clear_stay_connected()
            login = LoginWindow(start_main_window)
            # Change to maximized or full screen here
            login.showMaximized()
    else:
        login = LoginWindow(start_main_window)
        # Change to maximized or full screen here
        login.showMaximized()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
