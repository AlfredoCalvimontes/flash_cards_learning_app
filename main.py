"""Main application entry point."""

import sys
from PySide6.QtWidgets import QApplication

def main():
    """Initialize and start the application."""
    app = QApplication(sys.argv)
    # TODO: Initialize main window
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())