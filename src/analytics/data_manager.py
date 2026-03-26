# src/analytics/data_manager.py
"""
Central data management for the analytics module.
Handles import/export from CSV/Excel/JSON and database operations.
Uses pandas DataFrames for analysis.
"""

import os
import sqlite3
import pandas as pd
from typing import Optional, Dict, Any

from src.db.storage_module import StorageModule  # reuse connection

class DataManager:
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the DataManager.
        If db_path is None, use the default from StorageModule.
        """
        self.storage = StorageModule(db_path) if db_path else StorageModule()
        self._data = {}  # cache DataFrames for products, costs, volumes

    # -------------------------------------------------------------------------
    # Import from files
    # -------------------------------------------------------------------------
    def import_from_csv(self, filepath: str, table_name: str, replace: bool = False) -> bool:
        """
        Import CSV file into the database table.
        table_name must be one of: 'products', 'costs', 'volumes', 'scenario_templates'
        If replace=True, clears the table before import.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        df = pd.read_csv(filepath)
        conn = self.storage._connect()
        try:
            if replace:
                conn.execute(f"DELETE FROM {table_name}")
            df.to_sql(table_name, conn, if_exists='append', index=False)
            conn.commit()
            # Invalidate cache for this table
            self._data.pop(table_name, None)
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def import_from_excel(self, filepath: str, sheet_name: str, table_name: str, replace: bool = False) -> bool:
        """Import Excel sheet into database."""
        df = pd.read_excel(filepath, sheet_name=sheet_name)
        conn = self.storage._connect()
        try:
            if replace:
                conn.execute(f"DELETE FROM {table_name}")
            df.to_sql(table_name, conn, if_exists='append', index=False)
            conn.commit()
            self._data.pop(table_name, None)
            return True
        finally:
            conn.close()

    def import_from_json(self, filepath: str, table_name: str, replace: bool = False) -> bool:
        """Import JSON file into database."""
        df = pd.read_json(filepath)
        conn = self.storage._connect()
        try:
            if replace:
                conn.execute(f"DELETE FROM {table_name}")
            df.to_sql(table_name, conn, if_exists='append', index=False)
            conn.commit()
            self._data.pop(table_name, None)
            return True
        finally:
            conn.close()

    # -------------------------------------------------------------------------
    # Export to files
    # -------------------------------------------------------------------------
    def export_to_csv(self, table_name: str, filepath: str) -> bool:
        """Export a database table to CSV."""
        df = self.get_table_as_df(table_name)
        df.to_csv(filepath, index=False)
        return True

    def export_to_excel(self, table_name: str, filepath: str, sheet_name: str = "Sheet1") -> bool:
        """Export to Excel."""
        df = self.get_table_as_df(table_name)
        df.to_excel(filepath, sheet_name=sheet_name, index=False)
        return True

    def export_to_json(self, table_name: str, filepath: str) -> bool:
        """Export to JSON."""
        df = self.get_table_as_df(table_name)
        df.to_json(filepath, orient='records', indent=2)
        return True

    # -------------------------------------------------------------------------
    # Database helpers
    # -------------------------------------------------------------------------
    def get_table_as_df(self, table_name: str) -> pd.DataFrame:
        """
        Retrieve a database table as a pandas DataFrame, using cache.
        """
        if table_name in self._data:
            return self._data[table_name]
        conn = self.storage._connect()
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        self._data[table_name] = df
        return df

    def clear_cache(self):
        """Clear all cached DataFrames."""
        self._data.clear()

    # -------------------------------------------------------------------------
    # Initial data loading (from Data/ folder)
    # -------------------------------------------------------------------------
    def load_initial_data(self, data_folder: str = "Data") -> None:
        """
        Load the initial CSV/JSON files from the Data folder into the database.
        This will replace existing data.
        """
        files = {
            'products': os.path.join(data_folder, 'produits.csv'),
            'costs': os.path.join(data_folder, 'couts.csv'),
            'volumes': os.path.join(data_folder, 'volumes.csv'),
            'scenario_templates': os.path.join(data_folder, 'scenarios.json')
        }
        for table, path in files.items():
            if os.path.exists(path):
                print(f"Loading {table} from {path}")
                if path.endswith('.csv'):
                    self.import_from_csv(path, table, replace=True)
                elif path.endswith('.json'):
                    self.import_from_json(path, table, replace=True)
                # Add Excel support if needed
            else:
                print(f"Warning: {path} not found")
        self.clear_cache()

    def insert_product(self, product_id, name, category, cost_price, selling_price):
        conn = self.storage._connect()
        try:
            conn.execute("""
                INSERT OR REPLACE INTO products (product_id, name, category, cost_price, selling_price)
                VALUES (?, ?, ?, ?, ?)
            """, (product_id, name, category, cost_price, selling_price))
            conn.commit()
            self.clear_cache()
        finally:
            conn.close()

    def insert_costs(self, product_id, fixed_costs, variable_costs, labor_costs, raw_materials):
        conn = self.storage._connect()
        try:
            conn.execute("""
                INSERT OR REPLACE INTO costs (product_id, fixed_costs, variable_costs, labor_costs, raw_materials)
                VALUES (?, ?, ?, ?, ?)
            """, (product_id, fixed_costs, variable_costs, labor_costs, raw_materials))
            conn.commit()
            self.clear_cache()
        finally:
            conn.close()

    def insert_volume(self, product_id, period, produced, sold):
        conn = self.storage._connect()
        try:
            conn.execute("""
                         INSERT INTO volumes (product_id, period, produced, sold)
                         VALUES (?, ?, ?, ?)
                         """, (product_id, period, produced, sold))
            conn.commit()
            self.clear_cache()
        finally:
            conn.close()