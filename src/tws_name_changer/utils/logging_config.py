"""Logging that avoids device identifiers and advertisement payloads."""
import logging
import sys


def configure_logging(debug: bool = False, log_to_file: bool = True) -> logging.Logger:
    """Configure the package logger.

    Sets up a stream handler on the ``tws_name_changer`` logger. When
    ``debug=True`` the level is lowered to DEBUG so that per-backend
    diagnostics (error codes, source counts, timing) are visible.
    When ``log_to_file=True``, a file handler in the user AppData directory
    is added if accessible.

    Privacy note: DEBUG logs include Bluetooth addresses from the local
    Windows paired-device registry and BLE advertisements. INFO logs
    record only device counts and error codes — no addresses or names.
    """
    logger = logging.getLogger("tws_name_changer")
    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        if log_to_file:
            try:
                from ..storage.settings import get_app_data_dir
                log_dir = get_app_data_dir()
                log_dir.mkdir(parents=True, exist_ok=True)
                file_handler = logging.FileHandler(log_dir / "tws_name_changer.log", encoding="utf-8")
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception:
                pass

    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    return logger



def configure_diagnostic_logging() -> logging.Logger:
    """Configure DEBUG-level logging for hardware troubleshooting.

    Equivalent to configure_logging(debug=True). Addresses and device
    names will appear in output. Use only for troubleshooting, not in
    production deployments.
    """
    return configure_logging(debug=True)
