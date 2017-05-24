# coding: utf-8
from loggingconf import logging, configure_logging
from config import DEFAULT_CONFIG
from app import create_app
from config import (
    WEB_SERVER_BIND_ADDRESS,
    WEB_SERVER_HOST, WEB_SERVER_PORT,
    EVE_API_PREFIX,
)


configure_logging()
logger = logging.getLogger(__name__)


def main():
    logger.info("WEB_SERVER_BIND_ADDRESS: %s" % WEB_SERVER_BIND_ADDRESS)
    logger.info("EVE_API_PREFIX: /{api}/{version}".format(api=EVE_API_PREFIX[0], version=EVE_API_PREFIX[1]))
    app = create_app(DEFAULT_CONFIG)
    app.run(host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == '__main__':
    main()

