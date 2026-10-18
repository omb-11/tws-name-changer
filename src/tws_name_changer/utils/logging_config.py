"""Logging that avoids device identifiers and advertisement payloads."""
import logging
import sys


def configure_logging(debug: bool = False) -> logging.Logger:
    """Configure the package logger.

    Sets up a stream handler on the ``tws_name_changer`` logger.  When
    ``debug=True`` the level is lowered to DEBUG so that per-backend
    diagnostics (error codes, source counts, timing) are visible.

    Privacy note: DEBUG logs include Bluetooth addresses from the local
    Windows paired-device registry and BLE advertisements.  INFO logs
    record only device counts and error codes — no addresses or names.
    """
    logger = logging.getLogger("tws_name_changer")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    return logger


def configure_diagnostic_logging() -> logging.Logger:
    """Configure DEBUG-level logging for hardware troubleshooting.

    Equivalent to configure_logging(debug=True). Addresses and device
    names will appear in output. Use only for troubleshooting, not in
    production deployments.
    """
    return configure_logging(debug=True)
