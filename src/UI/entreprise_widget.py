# src/ui/entreprise_widget.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QScrollArea, QFrame, QTabWidget, QTableWidget,
                             QTableWidgetItem, QMessageBox, QGridLayout, QHeaderView)
from PyQt6.QtCore import Qt
from src.modules.costing_module import CostingModule
from src.modules.analysis_module import AnalysisModule
from src.analytics.data_manager import DataManager
from datetime import datetime


class EntrepriseWidget(QWidget):
    def __init__(self, storage, company_data):
        super().__init__()
        self.storage = storage
        self.company_data = company_data
        self.data_manager = DataManager()  # reuse the same DB

        # Global style for this widget
        self.setStyleSheet("""
            QWidget { background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', sans-serif; }
            QFrame#Card { background: #161b22; border: 1px solid #30363d; border-radius: 12px; }
            QLabel#Header { color: #f0f6fc; font-size: 24px; font-weight: 700; }
            QLabel#SectionTitle { color: #a3e635; font-size: 16px; font-weight: 600; margin-top: 10px; }
            QLineEdit { 
                background: #0d1117; border: 1px solid #30363d; border-radius: 6px; 
                padding: 8px 12px; color: #f0f6fc; font-size: 13px;
            }
            QLineEdit:focus { border: 1px solid #a3e635; }
            QPushButton {
                background: #21262d; border: 1px solid #30363d; color: #c9d1d9;
                padding: 8px 16px; border-radius: 6px; font-weight: 600;
            }
            QPushButton:hover { background: #30363d; border-color: #8b949e; }
            QPushButton#Primary { background: #a3e635; color: #0d1117; border: none; }
            QPushButton#Primary:hover { background: #b4f156; }
            QScrollArea { border: none; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # Title
        title = QLabel("Paramètres Financiers")
        title.setObjectName("Header")
        main_layout.addWidget(title)

        desc = QLabel("Saisissez vos données de coûts pour générer l'analyse de rentabilité.")
        desc.setStyleSheet("color: #8b949e; font-size: 14px; margin-bottom: 20px;")
        main_layout.addWidget(desc)

        # Scroll Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)
        content_layout = QVBoxLayout(container)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 0, 20, 0)

        # Input Card
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #30363d; border-radius: 8px; background: #161b22; top: -1px; }
            QTabBar::tab {
                background: #0d1117; border: 1px solid #30363d; color: #8b949e;
                padding: 10px 20px; border-top-left-radius: 6px; border-top-right-radius: 6px;
                margin-right: 4px;
            }
            QTabBar::tab:selected { background: #161b22; color: #a3e635; border-bottom: 1px solid #161b22; }
        """)

        # Fields dictionaries
        self.fields_cf = {}
        self.fields_cv = {}
        self.fields_params = {}
        self.product_name_input = None  # will be set in create_params_tab

        self.tab1 = self.create_form_tab(
            ["Loyer + charges", "Salaires permanents", "Amortissements", "Assurances & Admin",
             "Frais financiers fixes"],
            self.fields_cf
        )
        self.tab2 = self.create_form_tab(
            ["Matières premières", "Main-d'œuvre directe", "Énergie & conso.", "Transport & logistique",
             "Contrôle qualité"],
            self.fields_cv
        )
        self.tab3 = self.create_params_tab()
        self.tabs.addTab(self.tab1, "Charges Fixes")
        self.tabs.addTab(self.tab2, "Charges Variables")
        self.tabs.addTab(self.tab3, "Paramètres")
        content_layout.addWidget(self.tabs)

        # Actions Bar
        actions_frame = QFrame()
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setContentsMargins(0, 10, 0, 10)

        btn_calc = QPushButton("Lancer le Calcul")
        btn_calc.setObjectName("Primary")
        btn_calc.clicked.connect(self.calculer)

        btn_reset = QPushButton("Réinitialiser")
        btn_reset.clicked.connect(self.reinitialiser)

        btn_save = QPushButton("Sauvegarder Scénario")
        btn_save.clicked.connect(self.sauvegarder)

        actions_layout.addWidget(btn_calc)
        actions_layout.addWidget(btn_save)
        actions_layout.addStretch()
        actions_layout.addWidget(btn_reset)
        content_layout.addWidget(actions_frame)

        # Results Section
        res_label = QLabel("Indicateurs de Performance")
        res_label.setObjectName("SectionTitle")
        content_layout.addWidget(res_label)

        res_card = QFrame()
        res_card.setObjectName("Card")
        res_layout = QVBoxLayout(res_card)
        res_layout.setContentsMargins(0, 0, 0, 0)
        res_layout.setSpacing(0)

        self.table = QTableWidget(6, 2)
        self.table.setHorizontalHeaderLabels(["Indicateur", "Valeur"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget { background: transparent; gridline-color: #30363d; border: none; }
            QHeaderView::section { background: #21262d; color: #c9d1d9; border: none; padding: 10px; font-weight: bold; }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid #30363d; }
        """)
        res_layout.addWidget(self.table)
        content_layout.addWidget(res_card)

        # Message / Advice Box
        self.message_box = QFrame()
        self.message_box.setStyleSheet("background: #1f242c; border-left: 4px solid #a3e635; border-radius: 4px;")
        msg_layout = QVBoxLayout(self.message_box)
        self.message_lbl = QLabel("")
        self.message_lbl.setWordWrap(True)
        self.message_lbl.setStyleSheet("color: #e6edf3; font-style: italic;")
        msg_layout.addWidget(self.message_lbl)
        self.message_box.hide()
        content_layout.addWidget(self.message_box)

        self.set_defaults()

    def create_form_tab(self, labels, storage_dict):
        """Create a tab with a 2‑column grid of labelled input fields."""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)

        for i, text in enumerate(labels):
            row = i // 2
            col = (i % 2) * 2

            lbl = QLabel(text)
            lbl.setStyleSheet("color: #8b949e; font-weight: 500;")

            inp = QLineEdit("0")
            storage_dict[text] = inp

            layout.addWidget(lbl, row, col)
            layout.addWidget(inp, row, col + 1)

        return widget

    def create_params_tab(self):
        """Custom tab for parameters, includes product name."""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)

        # Product name field
        lbl_name = QLabel("Nom du produit")
        lbl_name.setStyleSheet("color: #8b949e; font-weight: 500;")
        self.product_name_input = QLineEdit("Produit personnalisé")
        self.product_name_input.setStyleSheet("background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 8px 12px;")
        layout.addWidget(lbl_name, 0, 0)
        layout.addWidget(self.product_name_input, 0, 1)

        # Other parameter fields
        param_labels = ["Prix de vente HT", "Quantité produite/vendue", "Taux de rebut (%)",
                        "Taux TVA (%)", "Capacité maximale"]
        for i, text in enumerate(param_labels):
            row = i // 2 + 1  # start from row 1
            col = (i % 2) * 2

            lbl = QLabel(text)
            lbl.setStyleSheet("color: #8b949e; font-weight: 500;")

            inp = QLineEdit("0")
            self.fields_params[text] = inp

            layout.addWidget(lbl, row, col)
            layout.addWidget(inp, row, col + 1)

        return widget

    def set_defaults(self):
        self.fields_cf["Loyer + charges"].setText("1250")
        self.fields_cf["Salaires permanents"].setText("3200")
        self.fields_cf["Amortissements"].setText("850")
        self.fields_cf["Assurances & Admin"].setText("420")
        self.fields_cf["Frais financiers fixes"].setText("0")

        self.fields_cv["Matières premières"].setText("18")
        self.fields_cv["Main-d'œuvre directe"].setText("12")
        self.fields_cv["Énergie & conso."].setText("5")
        self.fields_cv["Transport & logistique"].setText("3")
        self.fields_cv["Contrôle qualité"].setText("0")

        self.fields_params["Prix de vente HT"].setText("45")
        self.fields_params["Quantité produite/vendue"].setText("1200")
        self.fields_params["Taux de rebut (%)"].setText("2")
        self.fields_params["Taux TVA (%)"].setText("20")
        self.fields_params["Capacité maximale"].setText("2000")

        self.product_name_input.setText("Produit personnalisé")
        self.message_box.hide()
        self.table.clearContents()

    def get_inputs(self):
        cf = sum(float(f.text() or "0") for f in self.fields_cf.values())
        cv = sum(float(f.text() or "0") for f in self.fields_cv.values())
        pv = float(self.fields_params["Prix de vente HT"].text() or "0")
        q = float(self.fields_params["Quantité produite/vendue"].text() or "0")
        return cf, cv, pv, q

    def calculer(self):
        try:
            cf, cv, pv, q = self.get_inputs()
            if pv <= 0 or q <= 0:
                raise ValueError("Prix de vente et quantité doivent être positifs.")
            costing = CostingModule(cf, cv, pv, q)
            analysis = AnalysisModule(costing)
            data = costing.to_dict()
            a_data = analysis.to_dict()

            self.table.setRowCount(6)

            items = [
                ("Coût Total (CT)", f"{data['cout total']:.2f} {self.company_data['devise']}"),
                ("Chiffre d'Affaires HT", f"{data['chiffre affaire']:.2f} {self.company_data['devise']}"),
                ("Bénéfice Net / Perte", f"{data['benefice']:.2f} {self.company_data['devise']}"),
                ("Seuil de rentabilité", f"{a_data['seuil rentabilite']:.0f} unités"),
                ("Marge sur CV", f"{data['marge sur cout variable']:.2f} {self.company_data['devise']}"),
                ("Taux de marge", f"{data['taux de marge']:.2f} %")
            ]

            for i, (label, val) in enumerate(items):
                self.table.setItem(i, 0, QTableWidgetItem(label))
                item_val = QTableWidgetItem(val)
                item_val.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                if i == 2:  # Bénéfice row
                    if data['benefice'] > 0:
                        item_val.setText(f"{val} ▲")
                    else:
                        item_val.setText(f"{val} ▼")
                self.table.setItem(i, 1, item_val)

            self.message_lbl.setText(f"💡 Conseil IA : {a_data['conseil']}")
            self.message_box.show()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur de saisie: {e}")

    def reinitialiser(self):
        self.set_defaults()

    def sauvegarder(self):
        """
        Sauvegarde le scénario courant dans la base de données (produits, coûts, volumes)
        pour qu'il soit visible dans les graphiques.
        """
        try:
            cf, cv, pv, q = self.get_inputs()
            product_name = self.product_name_input.text().strip()
            if not product_name:
                product_name = f"Scénario du {datetime.now().strftime('%d/%m/%Y %H:%M')}"

            # Générer un identifiant unique
            product_id = f"CUSTOM_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Insérer le produit
            self.data_manager.insert_product(
                product_id=product_id,
                name=product_name,
                category="Personnalisé",
                cost_price=cv,          # coût de revient unitaire = cv
                selling_price=pv
            )

            # Insérer les coûts
            self.data_manager.insert_costs(
                product_id=product_id,
                fixed_costs=cf,
                variable_costs=cv,
                labor_costs=cv * 0.5,   # répartition approximative
                raw_materials=cv * 0.5
            )

            # Optionnel : insérer un volume de vente basé sur la quantité saisie
            # Pour l'instant, on peut ajouter une ligne dans volumes avec la période courante
            current_period = datetime.now().strftime('%Y-%m')
            self.data_manager.insert_volume(
                product_id=product_id,
                period=current_period,
                produced=q,
                sold=q
            )

            QMessageBox.information(
                self,
                "Succès",
                f"Scénario '{product_name}' sauvegardé.\n"
                "Il apparaîtra dans les graphiques après rafraîchissement."
            )

            # Rafraîchir les données en cache (pour que les prochains graphiques les voient)
            self.data_manager.clear_cache()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde: {e}")