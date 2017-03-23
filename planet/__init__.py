# coding=utf-8


import logging
import os
import sys

import config
import publish

sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'vendor'))
import feedparser

xmlns = 'http://planet.intertwingly.net/'

logging.getLogger(__name__).addHandler(logging.NullHandler())

logger = logging.getLogger(__name__)
loggerParms = None

config.__init__()


def getLogger(level, log_format):
    """ get a logger with the specified log level """
    global logger, loggerParms
    if logger and loggerParms == (level, log_format):
        return logger

    logging.basicConfig(format=log_format)

    logger = logging.getLogger("planet.runner")
    logger.setLevel(logging.getLevelName(level))

    loggerParms = (level, log_format)
    return logger


# Configure feed parser
feedparser.SANITIZE_HTML = 1
feedparser.RESOLVE_RELATIVE_URIS = 0
