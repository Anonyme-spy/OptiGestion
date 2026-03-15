"""Main entry point for the OptiGestion PyQt6 desktop application."""

from __future__ import annotations

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow


def main() -> int:
	"""Create and run the OptiGestion desktop application."""
	app = QApplication(sys.argv)

	window = QMainWindow()
	window.setWindowTitle("OptiGestion")
	window.resize(800, 600)

	label = QLabel("OptiGestion - Application démarrée avec succès")
	label.setAlignment(Qt.AlignmentFlag.AlignCenter)
	window.setCentralWidget(label)

	window.show()
	return app.exec()


if __name__ == "__main__":
	raise SystemExit(main())
