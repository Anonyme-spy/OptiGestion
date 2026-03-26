from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame
)
from PyQt6.QtGui import QCursor, QPixmap
from PyQt6.QtCore import Qt, QPropertyAnimation
import sys

class Sidebar(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(64)
        self.setStyleSheet("background:#161b22; border-right:1px solid #333;")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        # Liste des items
        items = [
            ("icons/home.png","          Accueil"),
            ("icons/briefcase.png","        Module Entreprise"),
            ("icons/users.png","           Consommateurs"),
            ("icons/chart.png","        Graphique"),
            ("icons/profile.png","        Profiles"),
            ("icons/logout.png","         Quitter")
        ]

        for icon_path,text in items:
            item_frame = QFrame()
            item_layout = QHBoxLayout(item_frame)
            item_layout.setContentsMargins(12,8,12,8)
            item_layout.setSpacing(12)

            # Icône (image PNG/SVG)
            icon = QLabel()
            pixmap = QPixmap(icon_path).scaled(24,24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon.setPixmap(pixmap)

            # Texte
            label = QLabel(text)
            label.setStyleSheet("color:#aaa;")

            item_layout.addWidget(icon)
            item_layout.addWidget(label)
            item_layout.addStretch()

            item_frame.setStyleSheet("""
                QFrame:hover { background:#21262d; }
                QLabel:hover { color:#a3e635; }
            """)

            self.layout.addWidget(item_frame)

        self.layout.addStretch()

        # Animation largeur
        self.anim = QPropertyAnimation(self, b"minimumWidth")
        self.anim.setDuration(350)

    def enterEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self.width())
        self.anim.setEndValue(220)
        self.anim.start()

    def leaveEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self.width())
        self.anim.setEndValue(64)
        self.anim.start()


class AccountWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Changer de compte - Annalyse Intelligente")
        self.setStyleSheet("background-color:#0d1117; border:none; color:#eee;")
        self.setMinimumSize(900, 600)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # --- Header ---
        header = QFrame()
        header.setStyleSheet("background:#a3e635; border-bottom:1px solid #222;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20,0,20,0)
        header_layout.setSpacing(12)

        # Logo image
        logo = QLabel()
        pixmap = QPixmap("icons/logo.png").scaled(40,40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setFixedSize(40,40)

        title = QLabel("Annalyse Intelligente")
        title.setStyleSheet("color:#111; font-weight:600; font-size:18px;")

        header_layout.addWidget(logo)
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addWidget(header)

        # --- Body avec sidebar + contenu scrollable ---
        body = QHBoxLayout()
        body.setContentsMargins(0,0,0,0)
        body.setSpacing(0)

        sidebar = Sidebar()
        body.addWidget(sidebar)

        # Zone scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none;")
        body.addWidget(scroll, 1)

        container = QWidget()
        scroll.setWidget(container)
        content_layout = QVBoxLayout(container)
        content_layout.setContentsMargins(24,24,24,24)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- Card principal ---
        card = QFrame()
        card.setStyleSheet("background:#161b22; border:1px solid #333; border-radius:10px;")
        card.setFixedWidth(480)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30,30,30,30)
        card_layout.setSpacing(16)

        # Avatar
        avatar = QLabel()
        pixmap_avatar = QPixmap("icons/avatar.png").scaled(120,120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        avatar.setPixmap(pixmap_avatar)
        avatar.setFixedSize(120,120)
        avatar.setStyleSheet("background:#222; border-radius:60px; margin-bottom:16px;")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignCenter)

        h1 = QLabel("Hi, Denji ff!")
        h1.setStyleSheet("color:#a3e635; border:none; font-size:20px; font-weight:bold;")
        h1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(h1)

        email = QLabel("Omahefarakotonarivo0@gmail.com")
        email.setStyleSheet("color:#aaa; font-size:14px; border:none; margin-bottom:20px;")
        email.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(email)

        btn_manage = QPushButton("Gérer mon compte")
        btn_manage.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_manage.setStyleSheet("""
            QPushButton {
                background:#21262d; color:#eee; border:1px solid #444;
                border-radius:8px; padding:12px; margin:20px 0;
            }
            QPushButton:hover { border-color:#a3e635; }
        """)
        card_layout.addWidget(btn_manage)

        # --- Switch account section ---
        switch_card = QFrame()
        switch_card.setStyleSheet("background:#0d1117; border-radius:8px;")
        switch_layout = QVBoxLayout(switch_card)
        switch_layout.setContentsMargins(16,16,16,16)
        switch_layout.setSpacing(12)

        switch_title = QLabel("Changer de compte")
        switch_title.setStyleSheet("color:#ddd; border:none; font-size:14px;")
        switch_layout.addWidget(switch_title)

        avatars_layout = QHBoxLayout()
        avatars_layout.setSpacing(16)

        # Exemple plusieurs comptes
        accounts = ["icons/avatar.png","icons/avatar2.png","icons/avatar3.png"]
        for i, path in enumerate(accounts):
            mini = QLabel()
            pixmap_mini = QPixmap(path).scaled(52,52, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            mini.setPixmap(pixmap_mini)
            mini.setFixedSize(52,52)
            style = "border-radius:26px; border:3px solid "
            style += "#a3e635;" if i==0 else "#222;"
            mini.setStyleSheet(style)
            avatars_layout.addWidget(mini)

        switch_layout.addLayout(avatars_layout)
        card_layout.addWidget(switch_card)

        # --- Boutons profils et déconnexion ---
        btn_profiles = QPushButton("Gérer les profils")
        btn_profiles.setStyleSheet("""
            QPushButton {
                background:#0d1117; color:#eee; border:none;
                padding:14px; border-radius:6px; text-align:left;
            }
            QPushButton:hover { background:#21262d; }
        """)
        card_layout.addWidget(btn_profiles)

        btn_logout = QPushButton("Déconnexion")
        btn_logout.setStyleSheet("""
            QPushButton {
                background:#0d1117; color:#eee; border:none;
                padding:14px; border-radius:6px; text-align:left;
            }
            QPushButton:hover { background:#21262d; }
        """)
        card_layout.addWidget(btn_logout)

        content_layout.addWidget(card)
        body.addLayout(content_layout)

        main_layout.addLayout(body)

        # --- Footer ---
        footer = QLabel("Projet CAE — Confidentiel | Version 1.0 — Mars 2026 | Aide | Contact")
        footer.setStyleSheet("background:#161b22; border-top:1px solid #333; color:#888; font-size:12px; padding:12px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(footer)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AccountWindow()
    win.show()
    sys.exit(app.exec())
