xmlns = 'http://planet.intertwingly.net/'

logger = None
loggerParms = None

import os, sys, re
import config
config.__init__()

from ConfigParser import ConfigParser
from urlparse import urljoin

def getLogger(level, format):
    """ get a logger with the specified log level """
    global logger, loggerParms
    if logger and loggerParms == (level,format): return logger

    try:
        import logging
        logging.basicConfig(format=format)
    except:
        import compat_logging as logging
        logging.basicConfig(format=format)

    logger = logging.getLogger("planet.runner")
    logger.setLevel(logging.getLevelName(level))
    try:
        logger.warning
    except:
        logger.warning = logger.warn

    loggerParms = (level,format)
    return logger

sys.path.insert(1, os.path.join(os.path.dirname(__file__),'vendor'))

# Configure feed parser
import feedparser
feedparser.SANITIZE_HTML=0
feedparser.RESOLVE_RELATIVE_URIS=0
