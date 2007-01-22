xmlns = 'http://planet.intertwingly.net/'

logger = None

import os, sys, re
import config
config.__init__()

from ConfigParser import ConfigParser
from urlparse import urljoin

def getLogger(level, format):
    """ get a logger with the specified log level """
    global logger
    if logger: return logger

    try:
        import logging
        logging.basicConfig(format=format)
    except:
        import compat_logging as logging
        logging.basicConfig(format=format)

    logging.getLogger().setLevel(logging.getLevelName(level))
    logger = logging.getLogger("planet.runner")
    try:
        logger.warning
    except:
        logger.warning = logger.warn

    return logger

# Configure feed parser
from planet import feedparser
feedparser.SANITIZE_HTML=0
feedparser.RESOLVE_RELATIVE_URIS=0
