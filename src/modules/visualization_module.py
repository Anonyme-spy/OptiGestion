"""PDF reporting utilities for scenario visualization.

This module creates a simple and reusable PDF report based on scenario data.
It is designed for integration with PyQt6 controllers/services.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
except ImportError as exc:  # pragma: no cover - environment dependent
    _REPORTLAB_IMPORT_ERROR = exc
else:
    _REPORTLAB_IMPORT_ERROR = None


_PRODUCTION_PARAMETER_KEYS = [
    "module",
    "cout_fixe",
    "cout_variable",
    "prix_vente",
    "quantite",
]

_INDICATOR_KEYS = [
    "cout_total",
    "chiffre_affaires",
    "benefice",
    "seuil_rentabilite",
]


def _validate_output_path(output_path: str) -> Path:
    """Validate and normalize the PDF output path."""
    if not output_path or not output_path.strip():
        raise ValueError("output_path must be a non-empty string.")

    path = Path(output_path).expanduser().resolve()

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Invalid output format for: {path}. Expected a .pdf file.")
    if path.exists() and path.is_dir():
        raise IsADirectoryError(f"Expected a file path but received a directory: {path}")

    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _rows_from_keys(data: dict[str, Any], keys: list[str]) -> list[list[str]]:
    """Convert selected dictionary keys into report table rows."""
    rows: list[list[str]] = [["Champ", "Valeur"]]
    for key in keys:
        value = data.get(key, "")
        rows.append([key, "" if value is None else str(value)])
    return rows


def _build_table(rows: list[list[str]]) -> Table:
    """Build a styled two-column report table."""
    table = Table(rows, colWidths=[180, 300], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3A5F")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.beige]),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def generate_pdf_report(data: dict[str, Any], output_path: str) -> None:
    """Generate a scenario PDF report with titles and tables.

    The report includes:
    - Scenario name
    - Production parameters
    - Calculated indicators

    A dedicated section is included for future matplotlib graph integration.
    If ``data`` provides a ``graph_paths`` list, image files are embedded now.

    Parameters
    ----------
    data:
        Scenario dictionary containing report values.
    output_path:
        Destination path for the generated PDF file.

    Raises
    ------
    ImportError
        If ReportLab is not installed.
    TypeError
        If ``data`` is not a dictionary.
    ValueError
        If required values are invalid.
    IsADirectoryError
        If ``output_path`` points to a directory.
    PermissionError
        If the file cannot be written.
    OSError
        If an I/O error occurs during generation.
    """
    if _REPORTLAB_IMPORT_ERROR is not None:
        raise ImportError(
            "ReportLab is required to generate PDF reports. "
            "Install it with: pip install reportlab"
        ) from _REPORTLAB_IMPORT_ERROR

    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary.")

    path = _validate_output_path(output_path)

    scenario_name = data.get("nom") or data.get("scenario_name") or "Scenario sans nom"

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    body_style = styles["BodyText"]

    story: list[Any] = [
        Paragraph("Rapport de Scenario", title_style),
        Spacer(1, 12),
        Paragraph(f"Nom du scenario : {scenario_name}", body_style),
        Spacer(1, 14),
        Paragraph("Parametres de production", heading_style),
        Spacer(1, 8),
        _build_table(_rows_from_keys(data, _PRODUCTION_PARAMETER_KEYS)),
        Spacer(1, 14),
        Paragraph("Indicateurs calcules", heading_style),
        Spacer(1, 8),
        _build_table(_rows_from_keys(data, _INDICATOR_KEYS)),
        Spacer(1, 14),
        Paragraph("Graphiques", heading_style),
        Spacer(1, 6),
    ]

    graph_paths = data.get("graph_paths")
    if isinstance(graph_paths, list) and graph_paths:
        for graph_path in graph_paths:
            graph_file = Path(str(graph_path)).expanduser().resolve()
            if graph_file.exists() and graph_file.is_file():
                story.append(Image(str(graph_file), width=460, height=220))
                story.append(Spacer(1, 10))
    else:
        story.append(
            Paragraph(
                "Section reservee a l'integration de graphiques matplotlib.",
                body_style,
            )
        )

    document = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    try:
        document.build(story)
    except PermissionError as exc:
        raise PermissionError(f"Permission denied while writing PDF file: {path}") from exc
    except OSError as exc:
        raise OSError(f"Unable to write PDF file: {path}") from exc


__all__ = ["generate_pdf_report"]
