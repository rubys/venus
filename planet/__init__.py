# coding=utf-8


import logging


import config
import publish

import sys
sys.path.insert(1, os.path.join(os.path.dirname(__file__),'vendor'))
import feedparser


xmlns = 'http://planet.intertwingly.net/'

logger = None
loggerParms = None

config.__init__()


def getLogger(level, format):
    """ get a logger with the specified log level """
    global logger, loggerParms
    if logger and loggerParms == (level, format):
        return logger

    logging.basicConfig(format=format)

    logger = logging.getLogger("planet.runner")
    logger.setLevel(logging.getLevelName(level))

    loggerParms = (level, format)
    return logger


# Configure feed parser
feedparser.SANITIZE_HTML = 1
feedparser.RESOLVE_RELATIVE_URIS = 0
