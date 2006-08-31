"""
Fetch either a single feed, or a set of feeds, normalize to Atom and XHTML,
and write each as a set of entries in a cache directory.
"""

# Standard library modules
import time, calendar, re, os
from xml.dom import minidom
# Planet modules
import planet, config, feedparser, reconstitute, shell

# Regular expressions to sanitise cache filenames
re_url_scheme    = re.compile(r'^\w+:/*(\w+:|www\.)?')
re_slash         = re.compile(r'[?/:]+')
re_initial_cruft = re.compile(r'^[,.]*')
re_final_cruft   = re.compile(r'[,.]*$')

def filename(directory, filename):
    """Return a filename suitable for the cache.

    Strips dangerous and common characters to create a filename we
    can use to store the cache in.
    """
    try:
        if re_url_scheme.match(filename):
            if isinstance(filename,str):
                filename=filename.decode('utf-8').encode('idna')
            else:
                filename=filename.encode('idna')
    except:
        pass
    filename = re_url_scheme.sub("", filename)
    filename = re_slash.sub(",", filename)
    filename = re_initial_cruft.sub("", filename)
    filename = re_final_cruft.sub("", filename)

    return os.path.join(directory, filename)

def write(xdoc, out):
    """ write the document out to disk """
    file = open(out,'w')
    file.write(xdoc)
    file.close()

def spiderFeed(feed):
    """ Spider (fetch) a single feed """

    # read cached feed info
    sources = config.cache_sources_directory()
    feed_source = filename(sources, feed)
    feed_info = feedparser.parse(feed_source)
    if feed_info.feed.get('planet_http_status',None) == '410': return

    # read feed itself
    modified = None
    try:
        modified=time.strptime(
            feed_info.feed.get('planet_http_last_modified', None))
    except:
        pass
    data = feedparser.parse(feed_info.feed.get('planet_http_location',feed),
        etag=feed_info.feed.get('planet_http_etag',None), modified=modified)

    # capture http status
    if not data.has_key("status"):
        if data.has_key("entries") and len(data.entries)>0:
            data.status = 200
        elif data.bozo and data.bozo_exception.__class__.__name__=='Timeout':
            data.status = 408
        else:
            data.status = 500
    data.feed['planet_http_status'] = str(data.status)

    # process based on the HTTP status code
    log = planet.logger
    if data.status == 301 and data.has_key("entries") and len(data.entries)>0:
        log.warning("Feed has moved from <%s> to <%s>", feed, data.url)
        data.feed['planet_http_location'] = data.url
    elif data.status == 304:
        return log.info("Feed %s unchanged", feed)
    elif data.status >= 400:
        feed_info.update(data.feed)
        data.feed = feed_info
        if data.status == 410:
            log.info("Feed %s gone", feed)
        elif data.status == 408:
            log.warning("Feed %s timed out", feed)
        else:
            log.error("Error %d while updating feed %s", data.status, feed)
    else:
        log.info("Updating feed %s", feed)

    # capture etag and last-modified information
    if data.has_key('headers'):
        if data.has_key('etag') and data.etag:
            data.feed['planet_http_etag'] = data.etag
            log.debug("E-Tag: %s", data.etag)
        if data.has_key('modified') and data.modified:
            data.feed['planet_http_last_modified'] = time.asctime(data.modified)
            log.debug("Last Modified: %s",
                data.feed['planet_http_last_modified'])

    # capture feed and data from the planet configuration file
    if not data.feed.has_key('links'): data.feed['links'] = list()
    for link in data.feed.links:
        if link.rel == 'self': break
    else:
        data.feed.links.append(feedparser.FeedParserDict(
            {'rel':'self', 'type':'application/atom+xml', 'href':feed}))
    for name, value in config.feed_options(feed).items():
        data.feed['planet_'+name] = value
    
    # write the feed info to the cache
    if not os.path.exists(sources): os.makedirs(sources)
    xdoc=minidom.parseString('''<feed xmlns:planet="%s"
      xmlns="http://www.w3.org/2005/Atom"/>\n''' % planet.xmlns)
    reconstitute.source(xdoc.documentElement, data.feed, data.bozo)
    write(xdoc.toxml('utf-8'), filename(sources, feed))
    xdoc.unlink()

    # write each entry to the cache
    cache = config.cache_directory()
    for entry in data.entries:

        # generate an id, if none is present
        if not entry.has_key('id') or not entry.id:
            entry['id'] = reconstitute.id(None, entry)
            if not entry['id']: continue

        # compute cache file name based on the id
        cache_file = filename(cache, entry.id)

        # get updated-date either from the entry or the cache (default to now)
        mtime = None
        if entry.has_key('updated_parsed'):
            mtime = calendar.timegm(entry.updated_parsed)
            if mtime > time.time(): mtime = None
        if not mtime:
            try:
                mtime = os.stat(cache_file).st_mtime
            except:
                mtime = time.time()
            entry['updated_parsed'] = time.gmtime(mtime)

        # apply any filters
        xdoc = reconstitute.reconstitute(data, entry)
        output = xdoc.toxml('utf-8')
        xdoc.unlink()
        for filter in config.filters():
            output = shell.run(filter, output, mode="filter")

        # write out and timestamp the results
        write(output, cache_file) 
        os.utime(cache_file, (mtime, mtime))

def spiderPlanet(configFile):
    """ Spider (fetch) an entire planet """
    config.load(configFile)
    log = planet.getLogger(config.log_level())
    planet.setTimeout(config.feed_timeout())

    for feed in config.subscriptions():
        spiderFeed(feed)
