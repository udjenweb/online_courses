# coding: utf-8
import logging
import logging.config
from config import LOG_FILE_PATH
from tools import (
    LOGGING_CONF_DEFAULT,
    create_file_handler,
    create_console_handler,
)


def configure_logging(level=logging.DEBUG):
    logging.config.dictConfig(LOGGING_CONF_DEFAULT)

    logging.root.setLevel(level)

    console_handler = create_console_handler()
    logging.root.addHandler(console_handler)

    if LOG_FILE_PATH:
        file_handler = create_file_handler(logfile_path=LOG_FILE_PATH)
        logging.root.addHandler(file_handler)

