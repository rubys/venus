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

type_map = {'text': 'text/plain', 'html': 'text/html',
    'xhtml': 'application/xhtml+xml'}

def scrub(feed, data):

    # some data is not trustworthy
    for tag in config.ignore_in_feed(feed).split():
        for entry in data.entries:
            if entry.has_key(tag): del entry[tag]
            if entry.has_key(tag + "_detail"): del entry[tag + "_detail"]
            if entry.has_key(tag + "_parsed"): del entry[tag + "_parsed"]

    # adjust title types
    if config.title_type(feed):
        title_type = config.title_type(feed)
        title_type = type_map.get(title_type, title_type)
        for entry in data.entries:
            if entry.has_key('title_detail'):
                entry.title_detail['type'] = title_type

    # adjust summary types
    if config.summary_type(feed):
        summary_type = config.summary_type(feed)
        summary_type = type_map.get(summary_type, summary_type)
        for entry in data.entries:
            if entry.has_key('summary_detail'):
                entry.summary_detail['type'] = summary_type

    # adjust content types
    if config.content_type(feed):
        content_type = config.content_type(feed)
        content_type = type_map.get(content_type, content_type)
        for entry in data.entries:
            if entry.has_key('content'):
                entry.content[0]['type'] = content_type

    # some people put html in author names
    if config.name_type(feed).find('html')>=0:
        from planet.shell.tmpl import stripHtml
        if data.feed.has_key('author_detail') and \
            data.feed.author_detail.has_key('name'):
            data.feed.author_detail['name'] = \
                str(stripHtml(data.feed.author_detail.name))
        for entry in data.entries:
            if entry.has_key('author_detail') and \
                entry.author_detail.has_key('name'):
                entry.author_detail['name'] = \
                    str(stripHtml(entry.author_detail.name))
            if entry.has_key('source'):
                source = entry.source
                if source.has_key('author_detail') and \
                    source.author_detail.has_key('name'):
                    source.author_detail['name'] = \
                        str(stripHtml(source.author_detail.name))

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
    
    # identify inactive feeds
    if config.activity_threshold(feed):
        activity_horizon = \
            time.gmtime(time.time()-86400*config.activity_threshold(feed))
        updated = [entry.updated_parsed for entry in data.entries
            if entry.has_key('updated_parsed')]
        updated.sort()
        if not updated or updated[-1] < activity_horizon:
            msg = "no activity in %d days" % config.activity_threshold(feed)
            log.info(msg)
            data.feed['planet_message'] = msg

    # report channel level errors
    if data.status == 403:
       data.feed['planet_message'] = "403: forbidden"
    elif data.status == 404:
       data.feed['planet_message'] = "404: not found"
    elif data.status == 408:
       data.feed['planet_message'] = "408: request timeout"
    elif data.status == 410:
       data.feed['planet_message'] = "410: gone"
    elif data.status == 500:
       data.feed['planet_message'] = "internal server error"
    elif data.status >= 400:
       data.feed['planet_message'] = "http status %s" % status

    # perform user configured scrub operations on the data
    scrub(feed, data)

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
        if not entry.has_key('updated_parsed'):
            if entry.has_key('published_parsed'):
                entry['updated_parsed'] = entry.published_parsed
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
        for filter in config.filters(feed):
            output = shell.run(filter, output, mode="filter")
            if not output: return

        # write out and timestamp the results
        write(output, cache_file) 
        os.utime(cache_file, (mtime, mtime))

def spiderPlanet():
    """ Spider (fetch) an entire planet """
    log = planet.getLogger(config.log_level())
    planet.setTimeout(config.feed_timeout())

    for feed in config.subscriptions():
        spiderFeed(feed)
