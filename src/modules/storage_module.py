"""SQLite persistence helpers for scenario data.

This module provides a small, reusable API for storing and retrieving scenarios.
Call ``init_database`` once at application startup (for example from your PyQt6
main window/controller) before using the other functions.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

_DB_PATH: Path | None = None

_TABLE_NAME = "scenarios"

# Lister les champs de scénario pour garantir une correspondance cohérente entre le code et la base de données, et éviter les erreurs de frappe dans les requêtes SQL
_SCENARIO_FIELDS = [
    "nom",
    "module",
    "cout_fixe",
    "cout_variable",
    "prix_vente",
    "quantite",
    "cout_total",
    "chiffre_affaires",
    "benefice",
    "seuil_rentabilite",
    "notes",
]

# Fonction pour initialiser la base de données SQLite et créer la table des scénarios si elle n'existe pas, elle vérifie que le chemin est valide et gère les exceptions liées à l'initialisation de la base de données
def init_database(db_path: str) -> None:
    global _DB_PATH

    if not db_path or not db_path.strip():
        raise ValueError("db_path must be a non-empty string.")

    path = Path(db_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(path) as connection:
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT,
                module TEXT,
                cout_fixe REAL,
                cout_variable REAL,
                prix_vente REAL,
                quantite REAL,
                cout_total REAL,
                chiffre_affaires REAL,
                benefice REAL,
                seuil_rentabilite REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
            """
        )
        connection.commit()

    _DB_PATH = path

# Fonction pour obtenir une connexion SQLite à la base de données initialisée, elle vérifie que la base de données a été initialisée avant de tenter de se connecter et gère les exceptions liées à la connexion à la base de données
def _get_connection() -> sqlite3.Connection:
    """Return a SQLite connection using the initialized database path."""
    if _DB_PATH is None:
        raise RuntimeError(
            "Database is not initialized. Call init_database(db_path) first."
        )

    connection = sqlite3.connect(_DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

# Fonction pour valider qu'un chemin de fichier existe et est un fichier, elle gère les exceptions liées à la validation du chemin
def save_scenario(data: dict[str, Any]) -> int:

    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary.")

    payload = {field: data.get(field) for field in _SCENARIO_FIELDS}

    placeholders = ", ".join(["?" for _ in _SCENARIO_FIELDS])
    columns = ", ".join(_SCENARIO_FIELDS)

    with _get_connection() as connection:
        cursor = connection.execute(
            f"INSERT INTO {_TABLE_NAME} ({columns}) VALUES ({placeholders})",
            tuple(payload[field] for field in _SCENARIO_FIELDS),
        )
        connection.commit()
        return int(cursor.lastrowid)

# Fonction pour charger tous les scénarios de la base de données, elle gère les exceptions liées à la lecture de la base de données et retourne une liste de dictionnaires représentant les scénarios
def load_scenarios() -> list[dict[str, Any]]:

    with _get_connection() as connection:
        cursor = connection.execute(
            f"SELECT * FROM {_TABLE_NAME} ORDER BY created_at DESC, id DESC"
        )
        rows = cursor.fetchall()

    return [dict(row) for row in rows]

# Fonction pour supprimer un scénario de la base de données en fonction de son ID, elle vérifie que l'ID est valide et gère les exceptions liées à la suppression du scénario
def delete_scenario(scenario_id: int) -> None:

    if not isinstance(scenario_id, int) or scenario_id <= 0:
        raise ValueError("scenario_id must be a positive integer.")

    with _get_connection() as connection:
        connection.execute(f"DELETE FROM {_TABLE_NAME} WHERE id = ?", (scenario_id,))
        connection.commit()


__all__ = [
    "init_database",
    "save_scenario",
    "load_scenarios",
    "delete_scenario",
]
