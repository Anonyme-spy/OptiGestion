# src/UI/app.py
import sys
from PyQt6.QtWidgets import QApplication
from src.UI.login_window import LoginWindow
from src.UI.main_window import MainWindow


def execute_app():
    # High DPI scaling for modern displays
    import os
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Global Font Fix (optional, depending on OS)
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)

    # State container to hold the windows
    state = {"login": None, "main": None}

    def on_login_success(company_data):
        # Close login, open main in maximized mode
        state["main"] = MainWindow(company_data)
        state["main"].showFullScreen()
        if state["login"]:
            state["login"].close()

    # Launch Login in maximized mode
    state["login"] = LoginWindow(on_login_success)
    state["login"].showFullScreen()

    sys.exit(app.exec())
