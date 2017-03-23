# coding=utf-8
""" Expunge old entries from a cache of entries """
import glob
import os
import sys
import traceback
from xml.dom import minidom

import feedparser

import config
import planet
from spider import filename


def expungeCache():
    """ Expunge old entries from a cache of entries """
    log = planet.logger

    log.info("Determining feed subscriptions")
    entry_count = {}
    sources = config.cache_sources_directory()
    for sub in config.subscriptions():
        data = feedparser.parse(filename(sources, sub))
        if 'id' not in data.feed.keys():
            continue
        if 'cache_keep_entries' in config.feed_options(sub).keys():
            entry_count[data.feed.id] = int(config.feed_options(sub)['cache_keep_entries'])
        else:
            entry_count[data.feed.id] = config.cache_keep_entries()

    log.info("Listing cached entries")
    cache = config.cache_directory()
    dir_ = [(os.stat(filepath).st_mtime, filepath) for filepath in glob.glob(cache + "/*") if not os.path.isdir(filepath)]
    dir_.sort()
    dir_.reverse()

    for mtime, filepath in dir_:

        try:
            entry = minidom.parse(filepath)
            # determine source of entry
            entry.normalize()
            sources = entry.getElementsByTagName('source')
            if not sources:
                # no source determined, do not delete
                log.debug("No source found for %s", filepath)
                continue
            ids = sources[0].getElementsByTagName('id')
            if not ids:
                # feed id not found, do not delete
                log.debug("No source feed id found for %s", filepath)
                continue
            if ids[0].childNodes[0].nodeValue in entry_count:
                # subscribed to feed, update entry count
                entry_count[ids[0].childNodes[0].nodeValue] = entry_count[ids[0].childNodes[0].nodeValue] - 1
                if entry_count[ids[0].childNodes[0].nodeValue] >= 0:
                    # maximum not reached, do not delete
                    log.debug("Maximum not reached for %s from %s",
                              filepath, ids[0].childNodes[0].nodeValue)
                    continue
                else:
                    # maximum reached
                    log.debug("Removing %s, maximum reached for %s",
                              filepath, ids[0].childNodes[0].nodeValue)
            else:
                # not subscribed
                log.debug("Removing %s, not subscribed to %s",
                          filepath, ids[0].childNodes[0].nodeValue)
            # remove old entry
            os.unlink(filepath)

        except Exception as e:
            print("WARNING: Broad exception caught. FIXME")
            print(e)
            print(traceback.print_exception(*sys.exc_info()))
            log.error("Error parsing %s", filepath)

# end of expungeCache()
