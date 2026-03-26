from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtSignal, QEasingCurve
from src.utils.utils import safe_pixmap

class Sidebar(QFrame):
    item_clicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setFixedWidth(70)
        self.setStyleSheet("""
            Sidebar {
                background: #0d1117;
                border-right: 1px solid #30363d;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 10)
        layout.setSpacing(10)

        self.items_map = {}

        # Menu Items
        menu_data = [
            ("home", "icons/home.png", "Accueil"),
            ("entreprise", "icons/briefcase.png", "Module Entreprise"),
            ("graphique", "icons/chart.png", "Analyse Graphique"),
            ("profil", "icons/profile.png", "Profil"),
            ("data", "icons/database.png", "Données")
        ]

        for key, icon_path, text in menu_data:
            self.add_menu_item(layout, key, icon_path, text, is_bottom=False)

        layout.addStretch()

        # Logout at bottom
        self.add_menu_item(layout, "logout", "icons/logout.png", "Déconnexion", is_bottom=True)

        # Animation
        self.anim = QPropertyAnimation(self, b"minimumWidth")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def add_menu_item(self, layout, key, icon_path, text, is_bottom=False):
        btn = QFrame()
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(50)

        btn.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border-radius: 6px;
                margin: 0px 5px;
            }}
            QFrame:hover {{
                background-color: {'#21262d' if not is_bottom else '#3b1212'};
            }}
        """)

        row = QHBoxLayout(btn)
        row.setContentsMargins(10, 0, 10, 0)
        row.setSpacing(15)

        icon_label = QLabel()
        pix = safe_pixmap(icon_path, 32)
        icon_label.setPixmap(pix)
        icon_label.setFixedSize(64, 64)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label_color = "#ff7b72" if is_bottom else "#c9d1d9"
        label = QLabel(text)
        label.setStyleSheet(f"color: {label_color}; font-weight: 500;")
        label.setVisible(False)

        row.addWidget(icon_label)
        row.addWidget(label)
        row.addStretch()

        btn.mousePressEvent = lambda e, k=key: self.item_clicked.emit(k)

        self.items_map[btn] = label
        layout.addWidget(btn)

    def enterEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self.width())
        self.anim.setEndValue(240)
        self.anim.start()
        for btn, label in self.items_map.items():
            label.setVisible(True)

    def leaveEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self.width())
        self.anim.setEndValue(70)
        self.anim.start()
        for btn, label in self.items_map.items():
            label.setVisible(False)