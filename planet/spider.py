"""
Fetch either a single feed, or a set of feeds, normalize to Atom and XHTML,
and write each as a set of entries in a cache directory.
"""

# Standard library modules
import time, calendar, re, os
# Planet modules
import config, feedparser, reconstitute

try:
    from xml.dom.ext import PrettyPrint
except:
    PrettyPrint = None

# Regular expressions to sanitise cache filenames
re_url_scheme    = re.compile(r'^[^:]*://')
re_slash         = re.compile(r'[?/]+')
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

def spiderFeed(feed):
    """ Spider (fetch) a single feed """
    data = feedparser.parse(feed)
    cache = config.cache_directory()

    # capture data from the planet configuration file
    for name, value in config.feed_options(feed).items():
        data.feed['planet:'+name] = value
    
    for entry in data.entries:
        if not entry.has_key('id'):
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

        xml = reconstitute.reconstitute(data, entry)
        
        file = open(out,'w')
        if PrettyPrint:
            PrettyPrint(reconstitute.reconstitute(data, entry), file)
        else:
            file.write(reconstitute.reconstitute(data, entry).toxml('utf-8'))
        file.close()

        os.utime(out, (mtime, mtime))

def spiderPlanet(configFile):
    """ Spider (fetch) an entire planet """
    import planet
    config.load(configFile)
    log = planet.getLogger(config.log_level())
    planet.setTimeout(config.feed_timeout())

    for feed in config.feeds():
        log.info("Updating feed %s", feed)
        spiderFeed(feed)
