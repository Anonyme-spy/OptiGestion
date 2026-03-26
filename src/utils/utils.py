# src/utils/utils.py
import os
import sys
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt

def get_project_root():
    """Return absolute path to project root (parent of src/)."""
    main_script = sys.modules['__main__'].__file__
    base = os.path.dirname(main_script)
    if os.path.basename(base) == 'src':
        base = os.path.dirname(base)
    return base

def safe_pixmap(relative_path, size=None, tint_color=None):
    """Load a pixmap, optionally scale and tint. Returns a blank pixmap if file not found."""
    full_path = os.path.join(get_project_root(), relative_path)
    pix = QPixmap(full_path)
    if pix.isNull():
        print(f"Warning: Icon not found: {full_path}")
        if size:
            pix = QPixmap(size, size)
            pix.fill(Qt.GlobalColor.transparent)
        else:
            pix = QPixmap(1, 1)
            pix.fill(Qt.GlobalColor.transparent)
        return pix

    if size:
        pix = pix.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio,
                         Qt.TransformationMode.SmoothTransformation)

    if tint_color:
        colored = QPixmap(pix.size())
        colored.fill(Qt.GlobalColor.transparent)
        painter = QPainter(colored)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        painter.drawPixmap(0, 0, pix)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(colored.rect(), QColor(tint_color))
        painter.end()
        pix = colored

    return pix