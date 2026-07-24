from functools import partial

from pawlogger import configure_loguru

from amherst.config import AMHERST_SETTINGS

logger = configure_loguru(log_file=AMHERST_SETTINGS.log_file, level=AMHERST_SETTINGS.log_level)
logger_from_settings = partial(configure_loguru, log_file=AMHERST_SETTINGS.log_file, level=AMHERST_SETTINGS.log_level)
