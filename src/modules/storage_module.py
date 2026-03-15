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

# Ordered fields used when inserting data.
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


def init_database(db_path: str) -> None:
    """Initialize the SQLite database and ensure table creation.

    Parameters
    ----------
    db_path:
        Path to the SQLite database file.

    Raises
    ------
    ValueError
        If ``db_path`` is empty.
    OSError
        If the parent directory cannot be created.
    sqlite3.Error
        If database initialization fails.
    """
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


def _get_connection() -> sqlite3.Connection:
    """Return a SQLite connection using the initialized database path."""
    if _DB_PATH is None:
        raise RuntimeError(
            "Database is not initialized. Call init_database(db_path) first."
        )

    connection = sqlite3.connect(_DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def save_scenario(data: dict[str, Any]) -> int:
    """Persist a scenario in the database.

    Parameters
    ----------
    data:
        Scenario payload. Supported keys are the scenario fields except ``id``
        and ``created_at``.

    Returns
    -------
    int
        The inserted scenario ID.

    Raises
    ------
    RuntimeError
        If the database has not been initialized.
    TypeError
        If ``data`` is not a dictionary.
    sqlite3.Error
        If the insert operation fails.
    """
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


def load_scenarios() -> list[dict[str, Any]]:
    """Load all scenarios ordered by newest first.

    Returns
    -------
    list[dict[str, Any]]
        A list of scenario records as dictionaries.

    Raises
    ------
    RuntimeError
        If the database has not been initialized.
    sqlite3.Error
        If the query fails.
    """
    with _get_connection() as connection:
        cursor = connection.execute(
            f"SELECT * FROM {_TABLE_NAME} ORDER BY created_at DESC, id DESC"
        )
        rows = cursor.fetchall()

    return [dict(row) for row in rows]


def delete_scenario(scenario_id: int) -> None:
    """Delete a scenario by its identifier.

    Parameters
    ----------
    scenario_id:
        ID of the scenario to remove.

    Raises
    ------
    RuntimeError
        If the database has not been initialized.
    ValueError
        If ``scenario_id`` is not a positive integer.
    sqlite3.Error
        If the delete operation fails.
    """
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
