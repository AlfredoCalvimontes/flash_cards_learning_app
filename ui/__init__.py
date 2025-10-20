"""UI package initialization."""

from PySide6.QtWidgets import QApplication

app = None

def get_app() -> QApplication:
    """Get or create the QApplication instance."""
    global app
    if app is None:
        app = QApplication([])
    return app

__all__ = ['get_app']
