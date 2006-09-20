xmlns = 'http://planet.intertwingly.net/'

logger = None

import os, sys, re
import config
config.__init__()

from ConfigParser import ConfigParser
from urlparse import urljoin

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
            logger.info("Socket timeout set to %d seconds", timeout)
        except ImportError:
            import socket
            if hasattr(socket, 'setdefaulttimeout'):
                logger.debug("timeoutsocket not found, using python function")
                socket.setdefaulttimeout(timeout)
                logger.info("Socket timeout set to %d seconds", timeout)
            else:
                logger.error("Unable to set timeout to %d seconds", timeout)

def downloadReadingList(list, orig_config, callback, use_cache=True, re_read=True):
    global logger
    try:

        import urllib2, StringIO
        from planet.spider import filename

        # list cache file name
        cache_filename = filename(config.cache_lists_directory(), list)

        # retrieve list options (e.g., etag, last-modified) from cache
        options = {}

        # add original options
        for key in orig_config.options(list):
            options[key] = orig_config.get(list, key)
            
        try:
            if use_cache:
                cached_config = ConfigParser()
                cached_config.read(cache_filename)
                for option in cached_config.options(list):
                     options[option] = cached_config.get(list,option)
        except:
            pass

        cached_config = ConfigParser()
        cached_config.add_section(list)
        for key, value in options.items():
            cached_config.set(list, key, value)

        # read list
        curdir=getattr(os.path, 'curdir', '.')
        if sys.platform.find('win') < 0:
            base = urljoin('file:', os.path.abspath(curdir))
        else:
            path = os.path.abspath(os.path.curdir)
            base = urljoin('file:///', path.replace(':','|').replace('\\','/'))

        request = urllib2.Request(urljoin(base + '/', list))
        if options.has_key("etag"):
            request.add_header('If-None-Match', options['etag'])
        if options.has_key("last-modified"):
            request.add_header('If-Modified-Since',
                options['last-modified'])
        response = urllib2.urlopen(request)
        if response.headers.has_key('etag'):
            cached_config.set(list, 'etag', response.headers['etag'])
        if response.headers.has_key('last-modified'):
            cached_config.set(list, 'last-modified',
                response.headers['last-modified'])

        # convert to config.ini
        data = StringIO.StringIO(response.read())

        if callback: callback(data, cached_config)

        # write to cache
        if use_cache:
            cache = open(cache_filename, 'w')
            cached_config.write(cache)
            cache.close()

        # re-parse and proceed
        logger.debug("Using %s readinglist", list) 
        if re_read:
            if use_cache:  
                orig_config.read(cache_filename)
            else:
                cdata = StringIO.StringIO()
                cached_config.write(cdata)
                cdata.seek(0)
                orig_config.readfp(cdata)
    except:
        try:
            if re_read:
                if use_cache:  
                    orig_config.read(cache_filename)
                else:
                    cdata = StringIO.StringIO()
                    cached_config.write(cdata)
                    cdata.seek(0)
                    orig_config.readfp(cdata)
                logger.info("Using cached %s readinglist", list)
        except:
            logger.exception("Unable to read %s readinglist", list)

