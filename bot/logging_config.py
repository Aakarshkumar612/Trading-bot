"""
logging_config.py
-----------------
Centralised logging setup.
- All DEBUG+ events go to logs/trading_bot.log
- INFO+ events go to the console (styled via Rich)
"""

import logging
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

_FORMATTER = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)-12s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_LOG_FILE = LOG_DIR / "trading_bot.log"
_initialised: set[str] = set()


def setup_logger(name: str) -> logging.Logger:
    """Return a named logger that writes to the shared log file and stdout."""
    logger = logging.getLogger(name)

    if name in _initialised:
        return logger

    logger.setLevel(logging.DEBUG)

    # ── File handler (DEBUG and above) ──────────────────────────────────────
    fh = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(_FORMATTER)

    # ── Console handler (INFO and above) ────────────────────────────────────
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(_FORMATTER)

    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.propagate = False

    _initialised.add(name)
    return logger


# Convenience root logger for the package
main_logger = setup_logger("trading_bot")
