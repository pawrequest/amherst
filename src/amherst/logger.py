from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger


def get_loguru(
        level: str = 'INFO',
        log_file : Path | None = None,
        color_dict: dict | None = None
) -> logger:
    terminal_format = log_fmt_local_terminal

    logger.remove()

    lvl = level.upper()
    if log_file:
        logger.add(log_file, rotation='1 day', delay=True, encoding='utf8', level=lvl)
    logger.add(sys.stderr, level=lvl, format=terminal_format)

    return logger
