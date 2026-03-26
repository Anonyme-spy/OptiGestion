# src/UI/login_window.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFrame, QMessageBox, QCheckBox,
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QColor, QFont
from src.db.storage_module import StorageModule
from src.utils.settings import save_stay_connected, clear_stay_connected


class LoginWindow(QWidget):
    def __init__(self, on_success_callback):
        super().__init__()
        self.on_success = on_success_callback
        self.storage = StorageModule()

        self.setWindowTitle("Connexion - OptiGestion")
        # Deeper dark background for modern feel
        self.setStyleSheet("background-color: #0d1117; color: #e6edf3; font-family: 'Segoe UI', system-ui, sans-serif;")
        self.setMinimumSize(800, 600)  # Slightly larger default so the card looks well-proportioned

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---------------- HEADER ----------------
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("background-color: #010409; border-bottom: 1px solid #30363d;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 0, 24, 0)
        header_layout.setSpacing(12)

        logo = QLabel("OG")
        logo.setFixedSize(36, 36)
        logo.setStyleSheet(
            "background-color: #a3e635; color: #010409; border-radius: 8px; font-weight: 800; font-size: 16px;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("OptiGestion")
        title.setStyleSheet("color: #e6edf3; font-weight: 700; font-size: 18px; border: none;")

        header_layout.addWidget(logo)
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addWidget(header)

        # ---------------- CONTENT ----------------
        content = QFrame()
        content_layout = QVBoxLayout(content)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # The Login Card
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #161b22; 
                border: 1px solid #30363d; 
                border-radius: 12px;
            }
        """)
        card.setFixedSize(420, 480)  # Better aspect ratio for a login pane

        # Add drop shadow to the card for depth
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 8)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(16)

        # Title
        h1 = QLabel("Bienvenue")
        h1.setStyleSheet("color: #ffffff; border: none; font-size: 24px; font-weight: 800;")
        h1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(h1)

        subtitle = QLabel("Connectez-vous à votre espace")
        subtitle.setStyleSheet("color: #8b949e; border: none; font-size: 14px; margin-bottom: 15px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(subtitle)

        # Email Input
        lbl_email = QLabel("Adresse email")
        lbl_email.setStyleSheet("color: #c9d1d9; border: none; font-size: 13px; font-weight: 600;")
        card_layout.addWidget(lbl_email)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("votre@email.com")
        self.email_input.setFixedHeight(45)
        self.email_input.setStyleSheet("""
            QLineEdit {
                background: #010409; border: 1px solid #30363d; 
                border-radius: 6px; padding: 0 15px; color: #c9d1d9;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #a3e635; background: #0d1117;
            }
        """)
        card_layout.addWidget(self.email_input)

        # Password Input
        lbl_pass = QLabel("Mot de passe")
        lbl_pass.setStyleSheet("color: #c9d1d9; border: none; font-size: 13px; font-weight: 600; margin-top: 5px;")
        card_layout.addWidget(lbl_pass)

        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setPlaceholderText("••••••••")
        self.pass_input.setFixedHeight(45)
        self.pass_input.setStyleSheet("""
            QLineEdit {
                background: #010409; border: 1px solid #30363d; 
                border-radius: 6px; padding: 0 15px; color: #c9d1d9;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #a3e635; background: #0d1117;
            }
        """)
        card_layout.addWidget(self.pass_input)

        # Stay connected checkbox
        self.stay_connected_cb = QCheckBox(" Rester connecté")
        self.stay_connected_cb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.stay_connected_cb.setStyleSheet("""
            QCheckBox {
                color: #8b949e; font-size: 13px; margin-top: 5px; border: none;
            }
            QCheckBox::indicator {
                width: 16px; height: 16px; border-radius: 4px;
                border: 1px solid #30363d; background: #010409;
            }
            QCheckBox::indicator:checked {
                background: #a3e635; border: 1px solid #a3e635;
            }
        """)
        card_layout.addWidget(self.stay_connected_cb)

        card_layout.addSpacing(10)

        # Login Button
        btn = QPushButton("Se Connecter")
        btn.setFixedHeight(45)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setStyleSheet("""
            QPushButton {
                background-color: #a3e635; color: #010409; 
                border: none; border-radius: 6px; font-weight: 700; font-size: 14px;
            }
            QPushButton:hover { background-color: #8bd22a; }
            QPushButton:pressed { background-color: #7ab824; }
        """)
        btn.clicked.connect(self.try_login)
        card_layout.addWidget(btn)

        # Registration Link
        switch = QLabel(
            "Pas encore de compte ? <a href='#' style='color: #a3e635; text-decoration: none;'>S'inscrire</a>")
        switch.setStyleSheet("color: #8b949e; border: none; font-size: 13px; margin-top: 10px;")
        switch.setAlignment(Qt.AlignmentFlag.AlignCenter)
        switch.setOpenExternalLinks(False)
        switch.linkActivated.connect(self.open_register)
        card_layout.addWidget(switch)

        card_layout.addStretch()

        content_layout.addWidget(card)
        main_layout.addWidget(content, 1)

        # ---------------- FOOTER ----------------
        footer = QLabel("Projet CAE — Confidentiel | Version 1.0 — Mars 2026 | Aide | Contact")
        footer.setStyleSheet(
            "background: #010409; border-top: 1px solid #30363d; color: #8b949e; font-size: 12px; padding: 12px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(footer)

    def try_login(self):
        email = self.email_input.text().strip()
        password = self.pass_input.text().strip()
        if not email or not password:
            QMessageBox.warning(self, "Champs manquants", "Veuillez remplir tous les champs.")
            return
        if self.storage.connecter_entreprise(email, password):
            with self.storage._connect() as conn:
                row = conn.execute("SELECT nom, secteur, email, devise FROM entreprise_account WHERE email = ?",
                                   (email,)).fetchone()
                if row:
                    company_data = dict(row)
                    print(f"Login successful for {email}, launching main window...")
                    # Handle stay connected
                    if self.stay_connected_cb.isChecked():
                        save_stay_connected(email, password)
                    else:
                        clear_stay_connected()
                    self.on_success(company_data)
                    self.close()
                else:
                    QMessageBox.critical(self, "Erreur", "Compte introuvable.")
        else:
            QMessageBox.critical(self, "Erreur", "Email ou mot de passe incorrect.")

    def open_register(self):
        from src.UI.register_window import RegisterWindow
        self.register_win = RegisterWindow(self.on_success)
        self.register_win.show()
