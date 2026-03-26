# src/ui/home_widget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor
import random

class HomeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color:#0a0a0a;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title = QLabel("Optimisez vos coûts\net boostez votre rentabilité")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("color: #a3e635; font-size: 36px; font-weight: bold;")

        self.text = QLabel(
            "Calculez votre seuil de rentabilité et prenez les meilleures décisions."
        )
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text.setStyleSheet("color: #dddddd; font-size: 16px;")

        self.button = QPushButton("Démarrer")
        self.button.setStyleSheet("""
            QPushButton {
                background-color: #a3e635;
                color: black;
                font-size: 20px;
                padding: 15px 40px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #84cc16;
            }
        """)
        self.button.clicked.connect(self.go_to_entreprise)

        layout.addWidget(self.title)
        layout.addWidget(self.text)
        layout.addSpacing(20)
        layout.addWidget(self.button)

        self.particles = [Particle(self.width(), self.height()) for _ in range(80)]
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_particles)
        self.timer.start(30)

    def go_to_entreprise(self):
        # Navigate to entreprise module in main window
        parent = self.parent()
        while parent and not hasattr(parent, 'switch_to_entreprise'):
            parent = parent.parent()
        if parent and hasattr(parent, 'switch_to_entreprise'):
            parent.switch_to_entreprise()
        else:
            print("Could not find main window to switch to entreprise module")

    def resizeEvent(self, event):
        for p in self.particles:
            p.width = self.width()
            p.height = self.height()
        return super().resizeEvent(event)

    def update_particles(self):
        for p in self.particles:
            p.move()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for p in self.particles:
            color = QColor(163, 230, 53)
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(p.x), int(p.y), p.size, p.size)

class Particle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.reset()

    def reset(self):
        self.x = random.randint(0, self.width) if self.width > 0 else 0
        self.y = random.randint(0, self.height) if self.height > 0 else 0
        self.size = random.randint(1, 4)
        self.dx = random.uniform(-0.5, 0.5)
        self.dy = random.uniform(-0.5, 0.5)

    def move(self):
        self.x += self.dx
        self.y += self.dy
        if self.x < 0 or self.x > self.width or self.y < 0 or self.y > self.height:
            self.reset()