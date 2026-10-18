"""Qt application startup and dependency wiring."""
import sys
from PySide6.QtWidgets import QApplication
from .bluetooth.discovery import BleakDiscoveryBackend, UnifiedDiscoveryBackend, WindowsPairedClassicBackend
from .services.rename_service import RenameService
from .ui.main_window import MainWindow

def run() -> int:
    application = QApplication(sys.argv)
    backend = UnifiedDiscoveryBackend(BleakDiscoveryBackend(), WindowsPairedClassicBackend())
    window = MainWindow(backend, RenameService())
    window.show()
    return application.exec()
