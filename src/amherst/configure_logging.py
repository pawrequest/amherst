import functools
import sys
from collections.abc import Callable
from datetime import timedelta
from pathlib import Path

from loguru import logger
from pawlogger.funcs import serializing_formatter


_SITE_PACKAGES = 'site-packages'


def ran_as_uv_tool() -> bool:
    here = __file__.lower().replace('/', '\\')
    return r'\uv\tools\amherst\lib\site-packages\amherst' in here


_RAN_AS_UV = ran_as_uv_tool()


def _display_path(path: str) -> str:
    """Relative to site-packages when running as a uv tool, else the full path."""
    if not _RAN_AS_UV:
        return path
    parts = Path(path).parts
    lowered = [p.lower() for p in parts]
    if _SITE_PACKAGES in lowered:
        idx = len(lowered) - 1 - lowered[::-1].index(_SITE_PACKAGES)
        return str(Path(*parts[idx + 1:]))
    return path


def loguru_ndjson_and_terminal(
        level: str = 'INFO',
        log_file: Path | None = None,
        rotation: timedelta = timedelta(weeks=1),
        retention: timedelta = timedelta(weeks=8),
):
    logger.remove()
    lvl = level.upper()
    config = {
        'level': lvl.upper(),
        'rotation': rotation,
        'retention': retention,
        'delay': True,
        'encoding': 'utf8',
    }
    if log_file and log_file.is_file():
        logger.add(log_file.with_suffix('.ndjson'), format=serializing_formatter, **config)
    logger.add(sys.stdout, level=lvl, format=log_fmt_local_terminal)
    # logger.add(sys.stderr, level=lvl, format=log_fmt_local_terminal)
    # logger.info(f'Configured loguru with level {lvl} and log_file {log_file}')


def log_fmt_local_terminal(record) -> str:
    name_txt = f'<lvl>{record["name"].split(".")[0]}</lvl>'
    lvltext = f'<lvl>{record["level"]}</lvl>'
    msg_txt = f'<lvl>{record["message"]}</lvl>'
    file_txt = f'"{_display_path(record["file"].path)}:{record["line"]}"'
    msg_txt = msg_txt.replace('{', '{{').replace('}', '}}')
    return f'{name_txt}({lvltext}) | {msg_txt} | {file_txt}\n'


def logger_wraps(*, entries=True, exits=True, level='DEBUG') -> Callable:
    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entries:
                logger_.log(level, f"Entering '{name}' (args={args}, kwargs={kwargs})")
            result = func(*args, **kwargs)
            if exits:
                logger_.log(level, "Exiting '{}' (result={})", name, result)
            return result

        return wrapped

    return wrapper


if __name__ == '__main__':
    print(f'{ran_as_uv_tool()=}')
    loguru_ndjson_and_terminal(level='DEBUG', log_file=Path('test_logger.log'))
    logger.info('Test loguru configuration')
    logger.warning('This is a warning message', extra={'a': 'b'})
    # pprint(f'{dir()=}')

# from functools import partial
#
# from pawlogger import configure_loguru
# from pawlogger.config_loguru3 import loguru_ndjson_and_terminal
#
# from amherst.config import AMHERST_SETTINGS
#
#
# # logger = configure_loguru(log_file=AMHERST_SETTINGS.log_file, level=AMHERST_SETTINGS.log_level)
# def amherst_logger():
#     loguru_ndjson_and_terminal(level='DEBUG', log_file=AMHERST_SETTINGS.log_file)
#
#
# logger = amherst_logger()
# logger_from_settings = partial(configure_loguru, log_file=AMHERST_SETTINGS.log_file, level=AMHERST_SETTINGS.log_level)
