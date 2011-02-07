"""
Fetch either a single feed, or a set of feeds, normalize to Atom and XHTML,
and write each as a set of entries in a cache directory.
"""

# Standard library modules
import time, calendar, re, os, urlparse
from xml.dom import minidom
# Planet modules
import planet, config, feedparser, reconstitute, shell, socket, scrub
from StringIO import StringIO 

try:
  from hashlib import md5
except:
  from md5 import new as md5

# Regular expressions to sanitise cache filenames
re_url_scheme    = re.compile(r'^\w+:/*(\w+:|www\.)?')
re_slash         = re.compile(r'[?/:|]+')
re_initial_cruft = re.compile(r'^[,.]*')
re_final_cruft   = re.compile(r'[,.]*$')

index = True

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
    if isinstance(filename,unicode):
        filename=filename.encode('utf-8')
    filename = re_url_scheme.sub("", filename)
    filename = re_slash.sub(",", filename)
    filename = re_initial_cruft.sub("", filename)
    filename = re_final_cruft.sub("", filename)

    # limit length of filename
    if len(filename)>250:
        parts=filename.split(',')
        for i in range(len(parts),0,-1):
            if len(','.join(parts[:i])) < 220:
                filename = ','.join(parts[:i]) + ',' + \
                    md5(','.join(parts[i:])).hexdigest()
                break
  
    return os.path.join(directory, filename)

def write(xdoc, out, mtime=None):
    """ write the document out to disk """
    file = open(out,'w')
    file.write(xdoc)
    file.close()
    if mtime: os.utime(out, (mtime, mtime))

def _is_http_uri(uri):
    parsed = urlparse.urlparse(uri)
    return parsed[0] in ['http', 'https']

def writeCache(feed_uri, feed_info, data):
    log = planet.logger
    sources = config.cache_sources_directory()
    blacklist = config.cache_blacklist_directory()

    # capture http status
    if not data.has_key("status"):
        if data.has_key("entries") and len(data.entries)>0:
            data.status = 200
        elif data.bozo and \
            data.bozo_exception.__class__.__name__.lower()=='timeout':
            data.status = 408
        else:
            data.status = 500

    activity_horizon = \
        time.gmtime(time.time()-86400*config.activity_threshold(feed_uri))

    # process based on the HTTP status code
    if data.status == 200 and data.has_key("url"):
        feed_info.feed['planet_http_location'] = data.url
        if data.has_key("entries") and len(data.entries) == 0:
            log.warning("No data %s", feed_uri)
            feed_info.feed['planet_message'] = 'no data'
        elif feed_uri == data.url:
            log.info("Updating feed %s", feed_uri)
        else:
            log.info("Updating feed %s @ %s", feed_uri, data.url)
    elif data.status == 301 and data.has_key("entries") and len(data.entries)>0:
        log.warning("Feed has moved from <%s> to <%s>", feed_uri, data.url)
        data.feed['planet_http_location'] = data.url
    elif data.status == 304 and data.has_key("url"):
        feed_info.feed['planet_http_location'] = data.url
        if feed_uri == data.url:
            log.info("Feed %s unchanged", feed_uri)
        else:
            log.info("Feed %s unchanged @ %s", feed_uri, data.url)

        if not feed_info.feed.has_key('planet_message'):
            if feed_info.feed.has_key('planet_updated'):
                updated = feed_info.feed.planet_updated
                if feedparser._parse_date_iso8601(updated) >= activity_horizon:
                    return
        else:
            if feed_info.feed.planet_message.startswith("no activity in"):
               return
            if not feed_info.feed.planet_message.startswith("duplicate") and \
               not feed_info.feed.planet_message.startswith("no data"):
               del feed_info.feed['planet_message']

    elif data.status == 410:
        log.info("Feed %s gone", feed_uri)
    elif data.status == 408:
        log.warning("Feed %s timed out", feed_uri)
    elif data.status >= 400:
        log.error("Error %d while updating feed %s", data.status, feed_uri)
    else:
        log.info("Updating feed %s", feed_uri)

    # if read failed, retain cached information
    if not data.get('version') and feed_info.get('version'):
        data.feed = feed_info.feed
        data.bozo = feed_info.feed.get('planet_bozo','true') == 'true'
        data.version = feed_info.feed.get('planet_format')
    data.feed['planet_http_status'] = str(data.status)

    # capture etag and last-modified information
    if data.has_key('headers'):
        if data.has_key('etag') and data.etag:
            data.feed['planet_http_etag'] = data.etag
        elif data.headers.has_key('etag') and data.headers['etag']:
            data.feed['planet_http_etag'] =  data.headers['etag']

        if data.headers.has_key('last-modified'):
            data.feed['planet_http_last_modified']=data.headers['last-modified']
        elif data.has_key('modified') and data.modified:
            data.feed['planet_http_last_modified'] = time.asctime(data.modified)

        if data.headers.has_key('-content-hash'):
            data.feed['planet_content_hash'] = data.headers['-content-hash']

    # capture feed and data from the planet configuration file
    if data.get('version'):
        if not data.feed.has_key('links'): data.feed['links'] = list()
        feedtype = 'application/atom+xml'
        if data.version.startswith('rss'): feedtype = 'application/rss+xml'
        if data.version in ['rss090','rss10']: feedtype = 'application/rdf+xml'
        for link in data.feed.links:
            if link.rel == 'self':
                link['type'] = feedtype
                break
        else:
            data.feed.links.append(feedparser.FeedParserDict(
                {'rel':'self', 'type':feedtype, 'href':feed_uri}))
    for name, value in config.feed_options(feed_uri).items():
        data.feed['planet_'+name] = value

    # perform user configured scrub operations on the data
    scrub.scrub(feed_uri, data)

    from planet import idindex
    global index
    if index != None: index = idindex.open()
 
    # select latest entry for each unique id
    ids = {}
    for entry in data.entries:
        # generate an id, if none is present
        if not entry.has_key('id') or not entry.id:
            entry['id'] = reconstitute.id(None, entry)
        elif hasattr(entry['id'], 'values'):
            entry['id'] = entry['id'].values()[0]
        if not entry['id']: continue

        # determine updated date for purposes of selection
        updated = ''
        if entry.has_key('published'): updated=entry.published
        if entry.has_key('updated'):   updated=entry.updated

        # if not seen or newer than last seen, select it
        if updated >= ids.get(entry.id,('',))[0]:
            ids[entry.id] = (updated, entry)

    # write each entry to the cache
    cache = config.cache_directory()
    for updated, entry in ids.values():

        # compute blacklist file name based on the id
        blacklist_file = filename(blacklist, entry.id)  

        # check if blacklist file exists. If so, skip it. 
        if os.path.exists(blacklist_file):
           continue

        # compute cache file name based on the id
        cache_file = filename(cache, entry.id)

        # get updated-date either from the entry or the cache (default to now)
        mtime = None
        if not entry.has_key('updated_parsed') or not entry['updated_parsed']:
            entry['updated_parsed'] = entry.get('published_parsed',None)
        if entry.has_key('updated_parsed'):
            try:
                mtime = calendar.timegm(entry.updated_parsed)
            except:
                pass
        if not mtime:
            try:
                mtime = os.stat(cache_file).st_mtime
            except:
                if data.feed.has_key('updated_parsed'):
                    try:
                        mtime = calendar.timegm(data.feed.updated_parsed)
                    except:
                        pass
        if not mtime: mtime = time.time()
        entry['updated_parsed'] = time.gmtime(mtime)

        # apply any filters
        xdoc = reconstitute.reconstitute(data, entry)
        output = xdoc.toxml().encode('utf-8')
        xdoc.unlink()
        for filter in config.filters(feed_uri):
            output = shell.run(filter, output, mode="filter")
            if not output: break
        if not output:
          if os.path.exists(cache_file): os.remove(cache_file)
          continue

        # write out and timestamp the results
        write(output, cache_file, mtime) 
    
        # optionally index
        if index != None: 
            feedid = data.feed.get('id', data.feed.get('link',None))
            if feedid:
                if type(feedid) == unicode: feedid = feedid.encode('utf-8')
                index[filename('', entry.id)] = feedid

    if index: index.close()

    # identify inactive feeds
    if config.activity_threshold(feed_uri):
        updated = [entry.updated_parsed for entry in data.entries
            if entry.has_key('updated_parsed')]
        updated.sort()

        if updated:
            data.feed['planet_updated'] = \
                time.strftime("%Y-%m-%dT%H:%M:%SZ", updated[-1])
        elif data.feed.has_key('planet_updated'):
           updated = [feedparser._parse_date_iso8601(data.feed.planet_updated)]

        if not updated or updated[-1] < activity_horizon:
            msg = "no activity in %d days" % config.activity_threshold(feed_uri)
            log.info(msg)
            data.feed['planet_message'] = msg

    # report channel level errors
    if data.status == 226:
        if data.feed.has_key('planet_message'): del data.feed['planet_message']
        if feed_info.feed.has_key('planet_updated'):
            data.feed['planet_updated'] = feed_info.feed['planet_updated']
    elif data.status == 403:
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
        data.feed['planet_message'] = "http status %s" % data.status

    # write the feed info to the cache
    if not os.path.exists(sources): os.makedirs(sources)
    xdoc=minidom.parseString('''<feed xmlns:planet="%s"
      xmlns="http://www.w3.org/2005/Atom"/>\n''' % planet.xmlns)
    reconstitute.source(xdoc.documentElement,data.feed,data.bozo,data.version)
    write(xdoc.toxml().encode('utf-8'), filename(sources, feed_uri))
    xdoc.unlink()

def httpThread(thread_index, input_queue, output_queue, log):
    import httplib2
    from httplib import BadStatusLine

    h = httplib2.Http(config.http_cache_directory())
    uri, feed_info = input_queue.get(block=True)
    while uri:
        log.info("Fetching %s via %d", uri, thread_index)
        feed = StringIO('')
        setattr(feed, 'url', uri)
        setattr(feed, 'headers', 
            feedparser.FeedParserDict({'status':'500'}))
        try:
            # map IRI => URI
            try:
                if isinstance(uri,unicode):
                    idna = uri.encode('idna')
                else:
                    idna = uri.decode('utf-8').encode('idna')
                if idna != uri: log.info("IRI %s mapped to %s", uri, idna)
            except:
                log.info("unable to map %s to a URI", uri)
                idna = uri

            # cache control headers
            headers = {}
            if feed_info.feed.has_key('planet_http_etag'):
                headers['If-None-Match'] = feed_info.feed['planet_http_etag']
            if feed_info.feed.has_key('planet_http_last_modified'):
                headers['If-Modified-Since'] = \
                    feed_info.feed['planet_http_last_modified']

            # issue request
            (resp, content) = h.request(idna, 'GET', headers=headers)

            # unchanged detection
            resp['-content-hash'] = md5(content or '').hexdigest()
            if resp.status == 200:
                if resp.fromcache:
                    resp.status = 304
                elif feed_info.feed.has_key('planet_content_hash') and \
                    feed_info.feed['planet_content_hash'] == \
                    resp['-content-hash']:
                    resp.status = 304

            # build a file-like object
            feed = StringIO(content) 
            setattr(feed, 'url', resp.get('content-location', uri))
            if resp.has_key('content-encoding'):
                del resp['content-encoding']
            setattr(feed, 'headers', resp)
        except BadStatusLine:
            log.error("Bad Status Line received for %s via %d",
                uri, thread_index)
        except httplib2.HttpLib2Error, e:
            log.error("HttpLib2Error: %s via %d", str(e), thread_index)
        except socket.error, e:
            if e.__class__.__name__.lower()=='timeout':
                feed.headers['status'] = '408'
                log.warn("Timeout in thread-%d", thread_index)
            else:
                log.error("HTTP Error: %s in thread-%d", str(e), thread_index)
        except Exception, e:
            import sys, traceback
            type, value, tb = sys.exc_info()
            log.error('Error processing %s', uri)
            for line in (traceback.format_exception_only(type, value) +
                traceback.format_tb(tb)):
                log.error(line.rstrip())

        output_queue.put(block=True, item=(uri, feed_info, feed))
        uri, feed_info = input_queue.get(block=True)

def spiderPlanet(only_if_new = False):
    """ Spider (fetch) an entire planet """
    log = planet.logger

    global index
    index = True

    timeout = config.feed_timeout()
    try:
        socket.setdefaulttimeout(float(timeout))
        log.info("Socket timeout set to %d seconds", timeout)
    except:
        try:
            import timeoutsocket
            timeoutsocket.setDefaultSocketTimeout(float(timeout))
            log.info("Socket timeout set to %d seconds", timeout)
        except:
            log.warning("Timeout set to invalid value '%s', skipping", timeout)

    from Queue import Queue
    from threading import Thread

    fetch_queue = Queue()
    parse_queue = Queue()

    threads = {}
    http_cache = config.http_cache_directory()
    # Should this be done in config?
    if http_cache and not os.path.exists(http_cache):
        os.makedirs(http_cache)


    if int(config.spider_threads()):
        # Start all the worker threads
        for i in range(int(config.spider_threads())):
            threads[i] = Thread(target=httpThread,
                args=(i,fetch_queue, parse_queue, log))
            threads[i].start()
    else:
        log.info("Building work queue")

    # Load the fetch and parse work queues
    for uri in config.subscriptions():
        # read cached feed info
        sources = config.cache_sources_directory()
        feed_source = filename(sources, uri)
        feed_info = feedparser.parse(feed_source)

        if feed_info.feed and only_if_new:
            log.info("Feed %s already in cache", uri)
            continue
        if feed_info.feed.get('planet_http_status',None) == '410':
            log.info("Feed %s gone", uri)
            continue

        if threads and _is_http_uri(uri):
            fetch_queue.put(item=(uri, feed_info))
        else:
            parse_queue.put(item=(uri, feed_info, uri))

    # Mark the end of the fetch queue
    for thread in threads.keys():
        fetch_queue.put(item=(None, None))

    # Process the results as they arrive
    feeds_seen = {}
    while fetch_queue.qsize() or parse_queue.qsize() or threads:
        while parse_queue.qsize():
            (uri, feed_info, feed) = parse_queue.get(False)
            try:

                if not hasattr(feed,'headers') or int(feed.headers.status)<300:
                    options = {}
                    if hasattr(feed_info,'feed'):
                        options['etag'] = \
                            feed_info.feed.get('planet_http_etag',None)
                        try:
                            modified=time.strptime(
                                feed_info.feed.get('planet_http_last_modified',
                                None))
                        except:
                            pass

                    data = feedparser.parse(feed, **options)
                else:
                    data = feedparser.FeedParserDict({'version': None,
                        'headers': feed.headers, 'entries': [], 'feed': {},
                        'href': feed.url, 'bozo': 0,
                        'status': int(feed.headers.status)})

                # duplicate feed?
                id = data.feed.get('id', None)
                if not id: id = feed_info.feed.get('id', None)

                href=uri
                if data.has_key('href'): href=data.href

                duplicate = None
                if id and id in feeds_seen:
                   duplicate = id
                elif href and href in feeds_seen:
                   duplicate = href

                if duplicate:
                    feed_info.feed['planet_message'] = \
                        'duplicate subscription: ' + feeds_seen[duplicate]
                    log.warn('Duplicate subscription: %s and %s' %
                        (uri, feeds_seen[duplicate]))
                    if href: feed_info.feed['planet_http_location'] = href

                if id: feeds_seen[id] = uri
                if href: feeds_seen[href] = uri

                # complete processing for the feed
                writeCache(uri, feed_info, data)

            except Exception, e:
                import sys, traceback
                type, value, tb = sys.exc_info()
                log.error('Error processing %s', uri)
                for line in (traceback.format_exception_only(type, value) +
                    traceback.format_tb(tb)):
                    log.error(line.rstrip())

        time.sleep(0.1)

        for index in threads.keys():
            if not threads[index].isAlive():
                del threads[index]
                if not threads:
                    log.info("Finished threaded part of processing.")
