# src/ui/main_window.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QVBoxLayout, QLabel, QFrame, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from src.UI.sidebar import Sidebar
from src.UI.home_widget import HomeWidget
from src.UI.entreprise_widget import EntrepriseWidget
from src.UI.graphique_widget import GraphiqueWidget
from src.UI.profil_widget import ProfilWidget
from src.db.storage_module import StorageModule

from src.UI.data_widget import DataTableWidget

class MainWindow(QMainWindow):
    def __init__(self, company_data):
        super().__init__()
        self.company_data = company_data
        self.storage = StorageModule()

        self.setWindowTitle("OptiGestion - " + company_data["nom"])
        self.setMinimumSize(1100, 700)
        self.setStyleSheet("background-color:#0d1117; color:#eee;")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.item_clicked.connect(self.on_sidebar_click)
        main_layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, 1)

        print("Creating widgets...")
        self.home_widget = HomeWidget()
        self.entreprise_widget = EntrepriseWidget(self.storage, company_data)
        self.graphique_widget = GraphiqueWidget(self.storage)
        self.profil_widget = ProfilWidget(company_data)

        self.stack.addWidget(self.home_widget)      # 0
        self.stack.addWidget(self.entreprise_widget) # 1
        self.stack.addWidget(self.graphique_widget)  # 2
        self.stack.addWidget(self.profil_widget)     # 3

        self.data_widget = DataTableWidget(self.storage)
        self.stack.addWidget(self.data_widget)  # index 4

        self.stack.setCurrentWidget(self.home_widget)
        print("Main window initialized.")

    def on_sidebar_click(self, key):
        if key == "home":
            self.stack.setCurrentWidget(self.home_widget)
        elif key == "entreprise":
            self.stack.setCurrentWidget(self.entreprise_widget)
        elif key == "graphique":
            self.stack.setCurrentWidget(self.graphique_widget)
        elif key == "profil":
            self.stack.setCurrentWidget(self.profil_widget)
        elif key == "logout":
            self.close()
        elif key == "data":
            self.stack.setCurrentWidget(self.data_widget)
            # Relaunch login window (handled in main.py)

    def switch_to_entreprise(self):
        self.stack.setCurrentWidget(self.entreprise_widget)

    def logout(self):
        self.close()

    def closeEvent(self, event):
        # Close any other top-level windows (like the hidden login window)
        for w in QApplication.topLevelWidgets():
            if w is not self:
                w.close()
        event.accept()