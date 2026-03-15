"""Input helpers for loading structured files into pandas DataFrames.

This module is designed to be reused by UI layers (including PyQt6) and
business modules. Functions raise clear exceptions so callers can display
user-friendly error messages in dialogs or status bars.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import pandas as pd


def _validate_path(file_path: str) -> Path:
    """Validate and normalize a file path.

    Parameters
    ----------
    file_path:
        Path to the input file.

    Returns
    -------
    pathlib.Path
        A normalized path object.

    Raises
    ------
    ValueError
        If ``file_path`` is empty.
    FileNotFoundError
        If the path does not exist.
    IsADirectoryError
        If the path points to a directory.
    """
    if not file_path or not file_path.strip():
        raise ValueError("file_path must be a non-empty string.")

    path = Path(file_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.is_dir():
        raise IsADirectoryError(f"Expected a file but received a directory: {path}")

    return path


def load_csv(file_path: str) -> pd.DataFrame:
    """Load data from a CSV file into a pandas DataFrame.

    Parameters
    ----------
    file_path:
        Path to a ``.csv`` file.

    Returns
    -------
    pandas.DataFrame
        Data loaded from the CSV file.

    Raises
    ------
    ValueError
        If the file extension is invalid or the CSV content is malformed.
    FileNotFoundError
        If the file does not exist.
    IsADirectoryError
        If the path points to a directory.
    PermissionError
        If the file cannot be accessed.
    """
    path = _validate_path(file_path)

    if path.suffix.lower() != ".csv":
        raise ValueError(f"Invalid CSV file format for: {path}. Expected a .csv file.")

    try:
        return pd.read_csv(path)
    except PermissionError as exc:
        raise PermissionError(f"Permission denied while reading CSV file: {path}") from exc
    except pd.errors.ParserError as exc:
        raise ValueError(f"Invalid CSV content in file: {path}") from exc
    except OSError as exc:
        raise OSError(f"Unable to read CSV file: {path}") from exc


def load_json(file_path: str) -> pd.DataFrame:
    """Load data from a JSON file into a pandas DataFrame.

    Parameters
    ----------
    file_path:
        Path to a ``.json`` file.

    Returns
    -------
    pandas.DataFrame
        Data loaded from the JSON file.

    Raises
    ------
    ValueError
        If the file extension is invalid or the JSON content is malformed.
    FileNotFoundError
        If the file does not exist.
    IsADirectoryError
        If the path points to a directory.
    PermissionError
        If the file cannot be accessed.
    """
    path = _validate_path(file_path)

    if path.suffix.lower() != ".json":
        raise ValueError(f"Invalid JSON file format for: {path}. Expected a .json file.")

    try:
        return pd.read_json(path)
    except PermissionError as exc:
        raise PermissionError(f"Permission denied while reading JSON file: {path}") from exc
    except ValueError as exc:
        raise ValueError(f"Invalid JSON content in file: {path}") from exc
    except OSError as exc:
        raise OSError(f"Unable to read JSON file: {path}") from exc


def export_to_csv(data: dict[str, Any], file_path: str) -> None:
    """Export a scenario dictionary to a CSV file with headers.

    Parameters
    ----------
    data:
        Scenario payload as a dictionary. Keys become CSV headers.
    file_path:
        Destination path for the ``.csv`` file.

    Raises
    ------
    TypeError
        If ``data`` is not a dictionary.
    ValueError
        If ``data`` is empty, ``file_path`` is empty, or extension is invalid.
    IsADirectoryError
        If ``file_path`` points to a directory.
    PermissionError
        If the file cannot be written.
    OSError
        If an I/O error occurs while writing the file.
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary.")
    if not data:
        raise ValueError("data cannot be empty.")
    if not file_path or not file_path.strip():
        raise ValueError("file_path must be a non-empty string.")

    path = Path(file_path).expanduser().resolve()

    if path.suffix.lower() != ".csv":
        raise ValueError(f"Invalid CSV file format for: {path}. Expected a .csv file.")
    if path.exists() and path.is_dir():
        raise IsADirectoryError(f"Expected a file path but received a directory: {path}")

    path.parent.mkdir(parents=True, exist_ok=True)

    headers = list(data.keys())
    row = {header: data.get(header) for header in headers}

    try:
        with path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()
            writer.writerow(row)
    except PermissionError as exc:
        raise PermissionError(f"Permission denied while writing CSV file: {path}") from exc
    except OSError as exc:
        raise OSError(f"Unable to write CSV file: {path}") from exc


__all__ = ["load_csv", "load_json", "export_to_csv"]
