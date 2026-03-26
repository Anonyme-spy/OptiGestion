# src/ui/graphique_widget.py (updated)
import sys
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QScrollArea, QFrame, QTabWidget,
                             QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.utils.utils import safe_pixmap
from src.modules.Visualisation_module import (
    charger_donnees,
    graphique_couts_marges,
    graphique_evolution_volumes,
    graphique_scenarios,
    graphique_seuil_rentabilite
)
from src.analytics.data_manager import DataManager

class GraphiqueWidget(QWidget):
    def __init__(self, storage):
        super().__init__()
        self.storage = storage
        self.data_manager = DataManager()
        self.setStyleSheet("background-color:#0d1117; color:#eee;")

        # We'll store the current graphs for later refresh
        self.donnees = None
        self.canvases = {}  # to store canvases for each tab

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet("background:#a3e635; border-bottom:1px solid #222;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(12)

        logo = QLabel()
        pix = safe_pixmap("icons/logo.png", 40)
        logo.setPixmap(pix)
        logo.setFixedSize(40, 40)

        title = QLabel("Analyse Graphique")
        title.setStyleSheet("color:#111; font-weight:600; font-size:18px;")

        # Refresh button
        self.refresh_btn = QPushButton("🔄 Actualiser les graphiques")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background:#21262d; color:#eee; border:1px solid #444;
                border-radius:6px; padding:6px 12px;
            }
            QPushButton:hover {
                background:#30363d;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_graphs)

        header_layout.addWidget(logo)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_btn)
        main_layout.addWidget(header)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none;")
        main_layout.addWidget(scroll, 1)

        container = QWidget()
        scroll.setWidget(container)
        content_layout = QVBoxLayout(container)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(20)

        # Top card with scenario selector
        top_card = QFrame()
        top_card.setStyleSheet("background:#161b22; border:1px solid #333; border-radius:10px;")
        top_layout = QHBoxLayout(top_card)
        top_layout.setContentsMargins(30, 20, 30, 20)
        top_layout.setSpacing(40)

        label_scenario = QLabel("Sélectionner un scénario:")
        label_scenario.setStyleSheet("color:#a3e635; font-weight:bold;")
        self.combo = QComboBox()
        self.combo.setStyleSheet(self.combo_style())
        top_layout.addWidget(label_scenario)
        top_layout.addWidget(self.combo)
        top_layout.addStretch()
        content_layout.addWidget(top_card)

        # Tabs for graphs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                background: #161b22;
                border: 1px solid #333;
                border-radius: 6px;
            }
            QTabBar::tab {
                background: #0d1117;
                color: #eee;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #161b22;
                border-bottom: 2px solid #a3e635;
            }
            QTabBar::tab:hover {
                background: #21262d;
            }
        """)

        content_layout.addWidget(self.tabs)

        # Footer
        footer = QLabel("Projet CAE — Confidentiel | Version 1.0 — Mars 2026 | Aide | Contact")
        footer.setStyleSheet("background:#161b22; border-top:1px solid #333; color:#888; font-size:12px; padding:12px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(footer)

        # Initial load
        self.load_data_and_graphs()

    def combo_style(self):
        return """
            QComboBox {
                background:#0d1117; color:#eee; border:1px solid #444; border-radius:6px;
                padding:6px 10px; min-width:200px;
            }
            QComboBox:hover { border-color:#a3e635; }
            QComboBox::drop-down { border:none; background:#21262d; width:20px; }
            QComboBox QAbstractItemView {
                background:#0d1117; border:1px solid #444;
                selection-background-color:#21262d; selection-color:#a3e635;
            }
        """

    def load_data_and_graphs(self):
        """Load data and generate graphs, then populate tabs."""
        try:
            # Clear cache to get fresh data
            self.data_manager.clear_cache()
            self.donnees = charger_donnees()

            # Populate scenario combo
            if self.donnees and self.donnees.get('scenarios') is not None:
                scenarios_df = self.donnees['scenarios']
                if not scenarios_df.empty:
                    self.combo.clear()
                    for name in scenarios_df['nom']:
                        self.combo.addItem(name)

            # Generate graphs
            fig1 = graphique_couts_marges(self.donnees)
            fig2 = graphique_evolution_volumes(self.donnees)
            fig3 = graphique_scenarios(self.donnees)
            fig4 = graphique_seuil_rentabilite(self.donnees)

            # Clear existing tabs
            self.tabs.clear()

            # Add new canvases
            if fig1:
                canvas1 = FigureCanvas(fig1)
                canvas1.setMinimumHeight(500)
                self.tabs.addTab(canvas1, "Coûts & Marges")
                self.canvases['couts_marges'] = canvas1
            else:
                self.tabs.addTab(self._error_label("Graphique Coûts & Marges indisponible"), "Coûts & Marges")

            if fig2:
                canvas2 = FigureCanvas(fig2)
                canvas2.setMinimumHeight(500)
                self.tabs.addTab(canvas2, "Évolution des volumes")
                self.canvases['evolution'] = canvas2
            else:
                self.tabs.addTab(self._error_label("Graphique Évolution des volumes indisponible"), "Évolution des volumes")

            if fig3:
                canvas3 = FigureCanvas(fig3)
                canvas3.setMinimumHeight(500)
                self.tabs.addTab(canvas3, "Comparaison scénarios")
                self.canvases['scenarios'] = canvas3
            else:
                self.tabs.addTab(self._error_label("Graphique Comparaison scénarios indisponible"), "Comparaison scénarios")

            if fig4:
                canvas4 = FigureCanvas(fig4)
                canvas4.setMinimumHeight(500)
                self.tabs.addTab(canvas4, "Seuil de rentabilité")
                self.canvases['seuil'] = canvas4
            else:
                self.tabs.addTab(self._error_label("Graphique Seuil de rentabilité indisponible"), "Seuil de rentabilité")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des données: {e}")

    def refresh_graphs(self):
        """Clear cache, reload data, and regenerate graphs."""
        try:
            # Clear cache
            self.data_manager.clear_cache()
            # Reload data
            self.load_data_and_graphs()
            QMessageBox.information(self, "Actualisation", "Les graphiques ont été actualisés avec les dernières données.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'actualisation: {e}")

    def _error_label(self, message):
        lbl = QLabel(message)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color: #888; padding: 50px;")
        return lbl