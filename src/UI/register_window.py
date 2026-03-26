# src/ui/register_window.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QComboBox, QFrame, QScrollArea, QMessageBox)
from PyQt6.QtCore import Qt
from src.db.storage_module import StorageModule

class RegisterWindow(QWidget):
    def __init__(self, on_success_callback):
        super().__init__()
        self.on_success = on_success_callback
        self.storage = StorageModule()

        self.setWindowTitle("Inscription - OptiGestion")
        self.setMinimumSize(500, 600)
        self.setStyleSheet("background-color: #0d1117; color: #eee; font-family: Arial;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = QFrame()
        header.setFixedHeight(58)
        header.setStyleSheet("background-color: #a3e635; border-bottom: 1px solid #222;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 0, 20, 0)
        h_layout.setSpacing(12)

        logo = QLabel("OG")
        logo.setFixedSize(40, 40)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("background:#111; color:#a3e635; border-radius:6px; font-weight:bold;")

        title = QLabel("Analyse Intelligente")
        title.setStyleSheet("color:#111; font-weight:600; font-size:22px;")

        h_layout.addWidget(logo)
        h_layout.addWidget(title)
        h_layout.addStretch()
        main_layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none;")
        main_layout.addWidget(scroll)

        content = QFrame()
        scroll.setWidget(content)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setStyleSheet("background-color:#161b22; border:1px solid #333; border-radius:10px;")
        card.setFixedSize(660, 780)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(16)

        h1 = QLabel("Inscription")
        h1.setStyleSheet("color:#a3e635; border:none; font-size:20px; font-weight:bold;")
        h1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(h1)

        self.entreprise = QLineEdit()
        self.entreprise.setPlaceholderText("Nom de l'entreprise")
        self.entreprise.setStyleSheet("padding:10px; background:#0d1117; border-radius:6px; color:#eee;")
        self.add_field("Nom de l'entreprise", self.entreprise, card_layout)

        self.secteur = QLineEdit()
        self.secteur.setPlaceholderText("Votre secteur")
        self.secteur.setStyleSheet("padding:10px; background:#0d1117; border-radius:6px; color:#eee;")
        self.add_field("Secteur d'activité", self.secteur, card_layout)

        self.devise = QComboBox()
        self.devise.addItems([
            "MGA - Ariary malgache",
            "EUR - Euro",
            "USD - Dollar américain",
            "XOF - Franc CFA",
            "GBP - Livre sterling"
        ])
        self.devise.setStyleSheet("padding:10px; background:#0d1117; border-radius:6px; color:#eee;")
        self.add_field("Devise principale", self.devise, card_layout)

        self.email = QLineEdit()
        self.email.setPlaceholderText("votre@email.com")
        self.email.setStyleSheet("padding:10px; background:#0d1117; border-radius:6px; color:#eee;")
        self.add_field("Email", self.email, card_layout)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("••••••••")
        self.password.setStyleSheet("padding:10px; background:#0d1117; border-radius:6px; color:#eee;")
        self.add_field("Mot de passe", self.password, card_layout)

        self.confirm = QLineEdit()
        self.confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm.setPlaceholderText("••••••••")
        self.confirm.setStyleSheet("padding:10px; background:#0d1117; border-radius:6px; color:#eee;")
        self.add_field("Confirmer votre mot de passe", self.confirm, card_layout)

        btn = QPushButton("Créer un compte")
        btn.setStyleSheet("""
            QPushButton {
                padding:12px 20px; border:none; border-radius:6px;
                font-weight:600; background:#a3e635; color:#111; margin:10px 0;
            }
            QPushButton:hover { background:#84cc16; }
        """)
        btn.clicked.connect(self.register)
        card_layout.addWidget(btn)

        switch = QLabel("Déjà un compte ? <a href='#'>Se connecter</a>")
        switch.setStyleSheet("border:none; color:#aaa;")
        switch.setAlignment(Qt.AlignmentFlag.AlignCenter)
        switch.linkActivated.connect(self.open_login)
        card_layout.addWidget(switch)

        content_layout.addWidget(card)

        footer = QLabel("Projet CAE — Confidentiel | Version 1.0 — Mars 2026 | Aide | Contact")
        footer.setStyleSheet("background:#161b22; border-top:1px solid #333; padding:12px; font-size:13px; color:#888;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(footer)

    def add_field(self, label_text, widget, layout):
        lbl = QLabel(label_text)
        lbl.setStyleSheet("color:#aaa; border:none; font-size:14px; margin-bottom:6px;")
        layout.addWidget(lbl)
        layout.addWidget(widget)

    def register(self):
        if self.password.text() != self.confirm.text():
            QMessageBox.warning(self, "Erreur", "Les mots de passe ne correspondent pas.")
            return
        if not all([self.entreprise.text(), self.secteur.text(), self.email.text(), self.password.text()]):
            QMessageBox.warning(self, "Champs manquants", "Veuillez remplir tous les champs.")
            return
        devise = self.devise.currentText().split(" - ")[0]
        success = self.storage.creer_compte_entreprise(
            self.entreprise.text(),
            self.secteur.text(),
            self.email.text(),
            self.password.text(),
            devise
        )
        if success:
            QMessageBox.information(self, "Succès", "Compte créé avec succès. Vous pouvez maintenant vous connecter.")
            company_data = {
                "nom": self.entreprise.text(),
                "secteur": self.secteur.text(),
                "email": self.email.text(),
                "devise": devise
            }
            self.on_success(company_data)
            self.close()
        else:
            QMessageBox.critical(self, "Erreur", "Un compte existe déjà. Veuillez vous connecter.")

    def open_login(self):
        self.close()
        from src.UI.login_window import LoginWindow
        self.login_win = LoginWindow(self.on_success)
        self.login_win.show()