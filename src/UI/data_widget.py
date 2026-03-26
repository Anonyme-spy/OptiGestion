# src/ui/data_widget.py
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QFrame, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox,
                             QFileDialog, QComboBox)
from PyQt6.QtCore import Qt
from src.analytics.data_manager import DataManager
import pandas as pd


class DataTableWidget(QWidget):
    def __init__(self, storage):
        super().__init__()
        self.storage = storage
        self.data_manager = DataManager()
        self.setStyleSheet("background-color:#0d1117; color:#eee;")

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
        from src.utils.utils import safe_pixmap
        pix = safe_pixmap("icons/logo.png", 40)
        logo.setPixmap(pix)
        logo.setFixedSize(40, 40)

        title = QLabel("Données d'Entreprise")
        title.setStyleSheet("color:#111; font-weight:600; font-size:18px;")

        # Import controls
        self.table_combo = QComboBox()
        self.table_combo.addItems(["products", "costs", "volumes", "scenario_templates"])
        self.table_combo.setStyleSheet("""
            QComboBox {
                background:#0d1117; color:#eee; border:1px solid #444; border-radius:6px;
                padding:6px 10px; min-width:150px;
            }
            QComboBox:hover { border-color:#a3e635; }
        """)

        btn_csv = QPushButton("📄 Importer CSV")
        btn_csv.setStyleSheet(self._button_style())
        btn_csv.clicked.connect(lambda: self.import_file("csv"))

        btn_excel = QPushButton("📊 Importer Excel")
        btn_excel.setStyleSheet(self._button_style())
        btn_excel.clicked.connect(lambda: self.import_file("excel"))

        btn_json = QPushButton("📋 Importer JSON")
        btn_json.setStyleSheet(self._button_style())
        btn_json.clicked.connect(lambda: self.import_file("json"))

        self.refresh_btn = QPushButton("🔄 Actualiser")
        self.refresh_btn.setStyleSheet(self._button_style())
        self.refresh_btn.clicked.connect(self.refresh_data)

        header_layout.addWidget(logo)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Importer dans:"))
        header_layout.addWidget(self.table_combo)
        header_layout.addWidget(btn_csv)
        header_layout.addWidget(btn_excel)
        header_layout.addWidget(btn_json)
        header_layout.addWidget(self.refresh_btn)
        main_layout.addWidget(header)

        # Scrollable table area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none;")
        main_layout.addWidget(scroll, 1)

        container = QWidget()
        scroll.setWidget(container)
        content_layout = QVBoxLayout(container)
        content_layout.setContentsMargins(24, 24, 24, 24)

        # Table
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #161b22;
                gridline-color: #30363d;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #0d1117;
                color: #a3e635;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 6px;
            }
        """)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        content_layout.addWidget(self.table)

        # Load initial data
        self.load_table_data()

    def _button_style(self):
        return """
            QPushButton {
                background:#21262d; color:#eee; border:1px solid #444;
                border-radius:6px; padding:6px 12px;
            }
            QPushButton:hover {
                background:#30363d;
            }
        """

    def import_file(self, file_type):
        """Open file dialog and import the selected file into the chosen table."""
        table = self.table_combo.currentText()
        if file_type == "csv":
            filter_str = "CSV files (*.csv)"
            method = self.data_manager.import_from_csv
        elif file_type == "excel":
            filter_str = "Excel files (*.xlsx *.xls)"
            method = self.data_manager.import_from_excel
        elif file_type == "json":
            filter_str = "JSON files (*.json)"
            method = self.data_manager.import_from_json
        else:
            return

        file_path, _ = QFileDialog.getOpenFileName(self, f"Importer {file_type.upper()}", "", filter_str)
        if not file_path:
            return

        try:
            if file_type == "excel":
                # For Excel, we need the sheet name – default to first sheet
                method(file_path, sheet_name=0, table_name=table, replace=False)
            else:
                method(file_path, table, replace=False)

            QMessageBox.information(self, "Succès", f"Données importées dans la table '{table}' avec succès.")
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'import: {e}")

    def load_table_data(self):
        """Fetch data from DataManager and populate table."""
        try:
            # Get products and costs
            products_df = self.data_manager.get_table_as_df('products')
            costs_df = self.data_manager.get_table_as_df('costs')
            volumes_df = self.data_manager.get_table_as_df('volumes')

            if products_df.empty:
                self.table.setRowCount(0)
                self.table.setColumnCount(0)
                self.table.setHorizontalHeaderLabels([])
                return

            # Merge products with costs
            merged = pd.merge(products_df, costs_df, on='product_id', how='left')

            # Aggregate volumes (sum sold per product)
            vol_sum = volumes_df.groupby('product_id')['sold'].sum().reset_index()
            merged = pd.merge(merged, vol_sum, on='product_id', how='left')
            merged.fillna(0, inplace=True)

            # Prepare columns
            columns = ['product_id', 'name', 'category', 'cost_price', 'selling_price',
                       'fixed_costs', 'variable_costs', 'sold']
            merged = merged[columns]

            # Set table dimensions
            self.table.setRowCount(len(merged))
            self.table.setColumnCount(len(columns))
            self.table.setHorizontalHeaderLabels([
                "ID", "Produit", "Catégorie", "Coût revient (Ar)", "Prix vente (Ar)",
                "Coûts fixes (Ar)", "Coûts variables (Ar)", "Volume vendu"
            ])

            # Populate table
            for i, row in merged.iterrows():
                for j, col in enumerate(columns):
                    value = row[col]
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    self.table.setItem(i, j, item)

            # Add summary row
            self.table.setRowCount(len(merged) + 1)
            summary_item = QTableWidgetItem("TOTAUX")
            summary_item.setBackground(Qt.GlobalColor.darkGray)
            self.table.setItem(len(merged), 0, summary_item)
            self.table.setItem(len(merged), 4, QTableWidgetItem(f"{merged['selling_price'].sum():.2f}"))
            self.table.setItem(len(merged), 5, QTableWidgetItem(f"{merged['fixed_costs'].sum():.2f}"))
            self.table.setItem(len(merged), 6, QTableWidgetItem(f"{merged['variable_costs'].sum():.2f}"))
            self.table.setItem(len(merged), 7, QTableWidgetItem(f"{merged['sold'].sum():.0f}"))

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des données: {e}")

    def refresh_data(self):
        """Clear cache and reload table data."""
        self.data_manager.clear_cache()
        self.load_table_data()
        QMessageBox.information(self, "Actualisation", "Données actualisées avec succès.")