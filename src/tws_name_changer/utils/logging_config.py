"""Logging that avoids device identifiers and advertisement payloads."""
import logging
def configure_logging() -> logging.Logger:
    logger = logging.getLogger("tws_name_changer")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
