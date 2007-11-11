""" Expunge old entries from a cache of entries """
import glob, os, planet, config, feedparser
from xml.dom import minidom
from spider import filename

def expungeCache():
    """ Expunge old entries from a cache of entries """
    log = planet.logger

    log.info("Determining feed subscriptions")
    entry_count = {}
    sources = config.cache_sources_directory()
    for sub in config.subscriptions():
        data=feedparser.parse(filename(sources,sub))
        if not data.feed.has_key('id'): continue
        if config.feed_options(sub).has_key('cache_keep_entries'):
            entry_count[data.feed.id] = int(config.feed_options(sub)['cache_keep_entries'])
        else:
            entry_count[data.feed.id] = config.cache_keep_entries()

    log.info("Listing cached entries")
    cache = config.cache_directory()
    dir=[(os.stat(file).st_mtime,file) for file in glob.glob(cache+"/*")
        if not os.path.isdir(file)]
    dir.sort()
    dir.reverse()

    for mtime,file in dir:

        try:
            entry=minidom.parse(file)
            # determine source of entry
            entry.normalize()
            sources = entry.getElementsByTagName('source')
            if not sources:
                # no source determined, do not delete
                log.debug("No source found for %s", file)
                continue
            ids = sources[0].getElementsByTagName('id')
            if not ids:
                # feed id not found, do not delete
                log.debug("No source feed id found for %s", file)
                continue
            if ids[0].childNodes[0].nodeValue in entry_count:
                # subscribed to feed, update entry count
                entry_count[ids[0].childNodes[0].nodeValue] = entry_count[
                    ids[0].childNodes[0].nodeValue] - 1
                if entry_count[ids[0].childNodes[0].nodeValue] >= 0:
                    # maximum not reached, do not delete
                    log.debug("Maximum not reached for %s from %s",
                        file, ids[0].childNodes[0].nodeValue)
                    continue
                else:
                    # maximum reached
                    log.debug("Removing %s, maximum reached for %s",
                        file, ids[0].childNodes[0].nodeValue)
            else:
                # not subscribed
                log.debug("Removing %s, not subscribed to %s",
                    file, ids[0].childNodes[0].nodeValue)
            # remove old entry
            os.unlink(file)

        except:
            log.error("Error parsing %s", file)

# end of expungeCache()
