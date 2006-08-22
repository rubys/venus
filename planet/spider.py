"""
Fetch either a single feed, or a set of feeds, normalize to Atom and XHTML,
and write each as a set of entries in a cache directory.
"""

# Standard library modules
import time, calendar, re, os
from xml.dom import minidom
# Planet modules
import planet, config, feedparser, reconstitute

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
    file.write(xdoc.toxml('utf-8'))
    file.close()
    xdoc.unlink()

def spiderFeed(feed):
    """ Spider (fetch) a single feed """
    data = feedparser.parse(feed)
    if not data.feed: return

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
    sources = config.cache_sources_directory()
    if not os.path.exists(sources): os.makedirs(sources)
    xdoc=minidom.parseString('''<feed xmlns:planet="%s"
      xmlns="http://www.w3.org/2005/Atom"/>\n''' % planet.xmlns)
    reconstitute.source(xdoc.documentElement, data.feed, data.bozo)
    write(xdoc, filename(sources, feed))

    # write each entry to the cache
    cache = config.cache_directory()
    for entry in data.entries:
        if not entry.has_key('id') or not entry.id:
            entry['id'] = reconstitute.id(None, entry)
            if not entry['id']: continue

        out = filename(cache, entry.id)

        if entry.has_key('updated_parsed'):
            mtime = calendar.timegm(entry.updated_parsed)
        else:
            try:
                mtime = os.stat(out).st_mtime
            except:
                mtime = time.time()
            entry['updated_parsed'] = time.gmtime(mtime)

        write(reconstitute.reconstitute(data, entry), out) 
        os.utime(out, (mtime, mtime))

def spiderPlanet(configFile):
    """ Spider (fetch) an entire planet """
    config.load(configFile)
    log = planet.getLogger(config.log_level())
    planet.setTimeout(config.feed_timeout())

    for feed in config.feeds():
        log.info("Updating feed %s", feed)
        spiderFeed(feed)
