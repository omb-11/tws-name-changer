"""Qt application startup and dependency wiring."""
import sys
from PySide6.QtWidgets import QApplication

from .bluetooth.discovery import BleakDiscoveryBackend, UnifiedDiscoveryBackend, WindowsPairedClassicBackend
from .services.rename_service import RenameService
from .storage.settings import Settings
from .ui.main_window import MainWindow
from .utils.logging_config import configure_logging


def run() -> int:
    logger = configure_logging()
    logger.info("TWS Name Changer application started")
    application = QApplication(sys.argv)
    application.setApplicationName("TWSNameChanger")
    backend = UnifiedDiscoveryBackend(BleakDiscoveryBackend(), WindowsPairedClassicBackend())
    settings = Settings()
    window = MainWindow(backend, RenameService(), settings)
    window.show()
    return application.exec()
