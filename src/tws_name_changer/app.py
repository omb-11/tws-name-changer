"""Qt application startup and dependency wiring."""
import sys
from PySide6.QtWidgets import QApplication
from .bluetooth.discovery import BleakDiscoveryBackend
from .services.rename_service import RenameService
from .ui.main_window import MainWindow

def run() -> int:
    application = QApplication(sys.argv)
    window = MainWindow(BleakDiscoveryBackend(), RenameService())
    window.show()
    return application.exec()
