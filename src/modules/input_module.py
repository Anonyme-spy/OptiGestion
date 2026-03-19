import csv
import json
from pathlib import Path
from typing import Any
import pandas as pd

# Charge un fichier CSV en DataFrame.
def load_csv(file_path: str) -> pd.DataFrame:
    path = Path(file_path).expanduser().resolve()
    return pd.read_csv(path)

# Charge un fichier JSON en DataFrame.
def load_json(file_path: str) -> pd.DataFrame:
    path = Path(file_path).expanduser().resolve()
    return pd.read_json(path)

# Exporte un dictionnaire vers un fichier CSV.
def export_to_csv(data: dict[str, Any], file_path: str) -> None:
    path = Path(file_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)

# Exporte un dictionnaire vers un fichier JSON.
def export_to_json(data: dict[str, Any], file_path: str) -> None:
    path = Path(file_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with path.open("w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=2, ensure_ascii=False)

__all__ = ["load_csv", "load_json", "export_to_csv", "export_to_json"]
