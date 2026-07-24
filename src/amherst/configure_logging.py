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
