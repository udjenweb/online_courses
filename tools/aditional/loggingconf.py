# coding: utf-8
import logging
import logging.handlers
import logging.config


LOGGING_CONF_DEFAULT = {
    'version': 1,
    'disable_existing_loggers': False,
}


# --- formatter(s) ---
FORMAT_DEFAULT = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'


# --- handler(s) ---
def create_file_handler(logfile_path, format=FORMAT_DEFAULT, level=logging.DEBUG):
    default_formatter = logging.Formatter(format)
    file_handler = logging.handlers.RotatingFileHandler(logfile_path,
                                                        maxBytes=10485760, backupCount=300, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(default_formatter)
    return file_handler


def create_console_handler(format=FORMAT_DEFAULT, level=logging.DEBUG):
    default_formatter = logging.Formatter(format)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(default_formatter)
    return console_handler


# for example usage :
# # --- configure(s) ---
# def configure_logging():
#     logging.config.dictConfig(LOGGING_CONF_DEFAULT)
#
#     logging.root.setLevel(logging.DEBUG)
#
#     console_handler = create_console_handler()
#     logging.root.addHandler(console_handler)
#
#     if LOG_FILE_PATH:
#         file_handler = create_file_handler(logfile_path=LOG_FILE_PATH)
#         logging.root.addHandler(file_handler)

