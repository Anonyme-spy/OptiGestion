# src/ui/profil_widget.py
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QFrame, QMessageBox, QCheckBox, QInputDialog, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from src.utils.utils import safe_pixmap, get_project_root
from src.utils.settings import get_stay_connected, save_stay_connected, clear_stay_connected
from src.db.storage_module import StorageModule

class ProfilWidget(QWidget):
    def __init__(self, company_data):
        super().__init__()
        self.company_data = company_data
        self.storage = StorageModule()
        self.setStyleSheet("background-color:#0d1117; color:#eee;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = QFrame()
        header.setStyleSheet("background:#a3e635; border-bottom:1px solid #222;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(12)

        logo = QLabel()
        pix = safe_pixmap("icons/logo.png", 40)
        logo.setPixmap(pix)
        logo.setFixedSize(40, 40)

        title = QLabel("Mon Compte")
        title.setStyleSheet("color:#111; font-weight:600; font-size:18px;")

        header_layout.addWidget(logo)
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none;")
        main_layout.addWidget(scroll, 1)

        container = QWidget()
        scroll.setWidget(container)
        content_layout = QVBoxLayout(container)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setStyleSheet("background:#161b22; border:1px solid #333; border-radius:10px;")
        card.setFixedWidth(480)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(16)

        # Avatar
        avatar = QLabel()
        avatar.setFixedSize(120, 120)
        avatar.setStyleSheet("background:#222; border-radius:60px; margin-bottom:16px;")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        avatar_path = os.path.join(get_project_root(), "icons", "profile.png")
        avatar_pix = QPixmap(avatar_path)
        if avatar_pix.isNull():
            avatar_pix = QPixmap(120, 120)
            avatar_pix.fill(Qt.GlobalColor.transparent)
            painter = QPainter(avatar_pix)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QColor("#a3e635"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(0, 0, 120, 120)
            painter.setPen(QColor("#111"))
            font = QFont()
            font.setPointSize(60)
            painter.setFont(font)
            painter.drawText(avatar_pix.rect(), Qt.AlignmentFlag.AlignCenter, self.company_data["nom"][0].upper())
            painter.end()
        else:
            avatar_pix = avatar_pix.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio,
                                           Qt.TransformationMode.SmoothTransformation)
        avatar.setPixmap(avatar_pix)
        card_layout.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignCenter)

        name_label = QLabel(company_data["nom"])
        name_label.setStyleSheet("color:#a3e635; font-size:20px; font-weight:bold;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(name_label)

        email_label = QLabel(company_data["email"])
        email_label.setStyleSheet("color:#aaa; font-size:14px; margin-bottom:20px;")
        email_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(email_label)

        # Stay connected toggle
        self.stay_connected_cb = QCheckBox("Rester connecté (connexion automatique)")
        self.stay_connected_cb.setStyleSheet("color:#aaa; margin: 10px 0;")
        # Set initial state
        stay, saved_email, _ = get_stay_connected()
        if stay and saved_email == company_data["email"]:
            self.stay_connected_cb.setChecked(True)
        else:
            self.stay_connected_cb.setChecked(False)
        self.stay_connected_cb.stateChanged.connect(self.on_stay_connected_toggled)
        card_layout.addWidget(self.stay_connected_cb)

        btn_manage = QPushButton("Gérer mon compte")
        btn_manage.setStyleSheet("""
            QPushButton {
                background:#21262d; color:#eee; border:1px solid #444;
                border-radius:8px; padding:12px; margin:20px 0;
            }
            QPushButton:hover { border-color:#a3e635; }
        """)
        btn_manage.clicked.connect(self.manage_account)
        card_layout.addWidget(btn_manage)

        btn_logout = QPushButton("Déconnexion")
        btn_logout.setStyleSheet("""
            QPushButton {
                background:#0d1117; color:#eee; border:none;
                padding:14px; border-radius:6px; text-align:left;
            }
            QPushButton:hover { background:#21262d; }
        """)
        btn_logout.clicked.connect(self.logout)
        card_layout.addWidget(btn_logout)

        content_layout.addWidget(card)

        footer = QLabel("Projet CAE — Confidentiel | Version 1.0 — Mars 2026 | Aide | Contact")
        footer.setStyleSheet("background:#161b22; border-top:1px solid #333; color:#888; font-size:12px; padding:12px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(footer)

    def on_stay_connected_toggled(self, state):
        if state == Qt.CheckState.Checked.value:
            # Check if we already have saved credentials for this user
            stay, saved_email, saved_password = get_stay_connected()
            if stay and saved_email == self.company_data["email"] and saved_password:
                # Already have credentials, do nothing
                pass
            else:
                # Need to prompt for password to enable
                password, ok = QInputDialog.getText(
                    self,
                    "Confirmation",
                    "Entrez votre mot de passe pour activer la connexion automatique:",
                    QLineEdit.EchoMode.Password
                )
                if ok and password:
                    # Verify password
                    if self.storage.connecter_entreprise(self.company_data["email"], password):
                        save_stay_connected(self.company_data["email"], password)
                    else:
                        QMessageBox.warning(self, "Erreur", "Mot de passe incorrect.")
                        self.stay_connected_cb.setChecked(False)
                else:
                    self.stay_connected_cb.setChecked(False)
        else:
            clear_stay_connected()

    def manage_account(self):
        QMessageBox.information(self, "Gestion du compte", "Fonctionnalité à venir.")

    def logout(self):
        # When logging out, clear the stay connected setting
        clear_stay_connected()
        parent = self.parent()
        while parent and not hasattr(parent, 'logout'):
            parent = parent.parent()
        if parent and hasattr(parent, 'logout'):
            parent.logout()
        else:
            self.window().close()