xmlns = 'http://planet.intertwingly.net/'

logger = None

import config
config.__init__()

def getLogger(level):
    """ get a logger with the specified log level """
    global logger
    if logger: return logger

    try:
        import logging
    except:
        import compat_logging as logging

    logging.basicConfig()
    logging.getLogger().setLevel(logging.getLevelName(level))
    logger = logging.getLogger("planet.runner")
    try:
        logger.warning
    except:
        logger.warning = logger.warn

    return logger


def setTimeout(timeout):
    """ time out rather than hang forever on ultra-slow servers."""
    if timeout:
        try:
            timeout = float(timeout)
        except:
            logger.warning("Timeout set to invalid value '%s', skipping", timeout)
            timeout = None

    if timeout:
        try:
            from planet import timeoutsocket
            timeoutsocket.setDefaultSocketTimeout(timeout)
            logger.debug("Socket timeout set to %d seconds", timeout)
        except ImportError:
            import socket
            if hasattr(socket, 'setdefaulttimeout'):
                logger.debug("timeoutsocket not found, using python function")
                socket.setdefaulttimeout(timeout)
                logger.debug("Socket timeout set to %d seconds", timeout)
            else:
                logger.error("Unable to set timeout to %d seconds", timeout)
