"""
Fetch either a single feed, or a set of feeds, normalize to Atom and XHTML,
and write each as a set of entries in a cache directory.
"""

# Standard library modules
import time, calendar, re, os, urlparse
from xml.dom import minidom
# Planet modules
import planet, config, feedparser, reconstitute, shell, socket
from StringIO import StringIO 

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
                import md5
                filename = ','.join(parts[:i]) + ',' + \
                    md5.new(','.join(parts[i:])).hexdigest()
                break
  
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
        if tag.find('lang')>=0: tag='language'
        if data.feed.has_key(tag): del data.feed[tag]
        for entry in data.entries:
            if entry.has_key(tag): del entry[tag]
            if entry.has_key(tag + "_detail"): del entry[tag + "_detail"]
            if entry.has_key(tag + "_parsed"): del entry[tag + "_parsed"]
            for key in entry.keys():
                if not key.endswith('_detail'): continue
                for detail in entry[key].copy():
                    if detail == tag: del entry[key][detail]

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
def _is_http_uri(uri):
    parsed = urlparse.urlparse(uri)
    return parsed[0] in ['http', 'https']

def spiderFeed(feed, only_if_new=0, content=None, resp_headers=None):
    """ Spider (fetch) a single feed """
    log = planet.logger

    # read cached feed info
    sources = config.cache_sources_directory()
    if not os.path.exists(sources):
        os.makedirs(sources, 0700)

    feed_source = filename(sources, feed)
    feed_info = feedparser.parse(feed_source)
    if feed_info.feed and only_if_new:
        log.info("Feed %s already in cache", feed)
        return
    if feed_info.feed.get('planet_http_status',None) == '410':
        log.info("Feed %s gone", feed)
        return

    # read feed itself
    if not resp_headers:
        modified = None
        try:
            modified=time.strptime(
                feed_info.feed.get('planet_http_last_modified', None))
        except:
            pass
        data = feedparser.parse(feed_info.feed.get('planet_http_location',feed),
            etag=feed_info.feed.get('planet_http_etag',None), modified=modified)
    elif int(resp_headers.status) < 300:
        # httplib2 was used to get the content, so prepare a 
        # proper object to pass to feedparser.
        f = StringIO(content) 
        setattr(f, 'url', resp_headers.get('content-location', feed))
        if resp_headers:
            if resp_headers.has_key('content-encoding'):
                del resp_headers['content-encoding']
            setattr(f, 'headers', resp_headers)
        data = feedparser.parse(f)
    else:
        data = feedparser.FeedParserDict({'status': int(resp_headers.status),
            'headers':resp_headers, 'version':None, 'entries': []})

    # capture http status
    if not data.has_key("status"):
        if data.has_key("entries") and len(data.entries)>0:
            data.status = 200
        elif data.bozo and data.bozo_exception.__class__.__name__.lower()=='timeout':
            data.status = 408
        else:
            data.status = 500

    activity_horizon = \
        time.gmtime(time.time()-86400*config.activity_threshold(feed))

    # process based on the HTTP status code
    if data.status == 200 and data.has_key("url"):
        data.feed['planet_http_location'] = data.url
        if feed == data.url:
            log.info("Updating feed %s", feed)
        else:
            log.info("Updating feed %s @ %s", feed, data.url)
    elif data.status == 301 and data.has_key("entries") and len(data.entries)>0:
        log.warning("Feed has moved from <%s> to <%s>", feed, data.url)
        data.feed['planet_http_location'] = data.url
    elif data.status == 304:
        log.info("Feed %s unchanged", feed)

        if not feed_info.feed.has_key('planet_message'):
            if feed_info.feed.has_key('planet_updated'):
                updated = feed_info.feed.planet_updated
                if feedparser._parse_date_iso8601(updated) >= activity_horizon:
                    return
        else:
            if feed_info.feed.planet_message.startswith("no activity in"):
               return
            del feed_info.feed['planet_message']

    elif data.status == 410:
        log.info("Feed %s gone", feed)
    elif data.status == 408:
        log.warning("Feed %s timed out", feed)
    elif data.status >= 400:
        log.error("Error %d while updating feed %s", data.status, feed)
    else:
        log.info("Updating feed %s", feed)

    # if read failed, retain cached information
    if not data.version and feed_info.version:
        data.feed = feed_info.feed
        data.bozo = feed_info.feed.get('planet_bozo','true') == 'true'
        data.version = feed_info.feed.get('planet_format')
    data.feed['planet_http_status'] = str(data.status)

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
    if data.version:
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
                {'rel':'self', 'type':feedtype, 'href':feed}))
    for name, value in config.feed_options(feed).items():
        data.feed['planet_'+name] = value

    # perform user configured scrub operations on the data
    scrub(feed, data)

    from planet import idindex
    global index
    if index != None: index = idindex.open()

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
        if not mtime or mtime > time.time(): mtime = time.time()
        entry['updated_parsed'] = time.gmtime(mtime)

        # apply any filters
        xdoc = reconstitute.reconstitute(data, entry)
        output = xdoc.toxml().encode('utf-8')
        xdoc.unlink()
        for filter in config.filters(feed):
            output = shell.run(filter, output, mode="filter")
            if not output: break
        if not output: continue

        # write out and timestamp the results
        write(output, cache_file) 
        os.utime(cache_file, (mtime, mtime))
    
        # optionally index
        if index != None: 
            feedid = data.feed.get('id', data.feed.get('link',None))
            if feedid:
                if type(feedid) == unicode: feedid = feedid.encode('utf-8')
                index[filename('', entry.id)] = feedid

    if index: index.close()

    # identify inactive feeds
    if config.activity_threshold(feed):
        updated = [entry.updated_parsed for entry in data.entries
            if entry.has_key('updated_parsed')]
        updated.sort()

        if updated:
            data.feed['planet_updated'] = \
                time.strftime("%Y-%m-%dT%H:%M:%SZ", updated[-1])
        elif data.feed.has_key('planet_updated'):
           updated = [feedparser._parse_date_iso8601(data.feed.planet_updated)]

        if not updated or updated[-1] < activity_horizon:
            msg = "no activity in %d days" % config.activity_threshold(feed)
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
    write(xdoc.toxml().encode('utf-8'), filename(sources, feed))
    xdoc.unlink()

def spiderPlanet(only_if_new = False):
    """ Spider (fetch) an entire planet """
    log = planet.getLogger(config.log_level(),config.log_format())

    global index
    index = True

    timeout = config.feed_timeout()
    try:
        socket.setdefaulttimeout(float(timeout))
    except:
        try:
            from planet import timeoutsocket
            timeoutsocket.setDefaultSocketTimeout(float(timeout))
            log.info("Socket timeout set to %d seconds", timeout)
        except:
            log.warning("Timeout set to invalid value '%s', skipping", timeout)

    if int(config.spider_threads()):
        from Queue import Queue, Empty
        from threading import Thread
        import httplib2
        from socket import gaierror, error 

        work_queue = Queue()
        awaiting_parsing = Queue()

        http_cache = config.http_cache_directory()
        if not os.path.exists(http_cache):
            os.makedirs(http_cache, 0700)

        def _spider_proc(thread_index):
            h = httplib2.Http(http_cache)
            try:
                while True:
                    # The non-blocking get will throw an exception when the queue 
                    # is empty which will terminate the thread.
                    uri = work_queue.get(block=False)
                    log.info("Fetching %s via %d", uri, thread_index)
                    resp = feedparser.FeedParserDict({'status':'500'})
                    content = None
                    try:
                        try:
                            if isinstance(uri,unicode):
                                idna = uri.encode('idna')
                            else:
                                idna = uri.decode('utf-8').encode('idna')
                            if idna != uri: log.info("IRI %s mapped to %s", uri, idna)
                        except:
                            log.info("unable to map %s to a URI", uri)
                            idna = uri
                        (resp, content) = h.request(idna)
                    except gaierror:
                        log.error("Fail to resolve server name %s via %d", uri, thread_index)
                    except error, e:
                        if e.__class__.__name__.lower()=='timeout':
                            resp['status'] = '408'
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
                    awaiting_parsing.put(block=True, item=(resp, content, uri))
 
            except Empty, e:
                log.info("Thread %d finished", thread_index)
                pass

        # Load the work_queue with all the HTTP(S) uris.
        map(work_queue.put, [uri for uri in config.subscriptions() if _is_http_uri(uri)])

        # Start all the worker threads
        threads = dict([(i, Thread(target=_spider_proc, args=(i,))) for i in range(int(config.spider_threads()))])
        for t in threads.itervalues():
            t.start()

        # Process the results as they arrive
        while work_queue.qsize() or awaiting_parsing.qsize() or threads:
            while awaiting_parsing.qsize() == 0 and threads:
                time.sleep(0.1)
            while awaiting_parsing.qsize():
                item = awaiting_parsing.get(False)
                try:
                    (resp_headers, content, uri) = item
                    if resp_headers.status == 200 and resp_headers.fromcache:
                        resp_headers.status = 304
                    spiderFeed(uri, only_if_new=only_if_new, content=content, resp_headers=resp_headers)
                except Exception, e:
                    import sys, traceback
                    type, value, tb = sys.exc_info()
                    log.error('Error processing %s', uri)
                    for line in (traceback.format_exception_only(type, value) +
                        traceback.format_tb(tb)):
                        log.error(line.rstrip())
            for index in threads.keys():
                if not threads[index].isAlive():
                    del threads[index]
    log.info("Finished threaded part of processing.")
                    

    # Process non-HTTP uris if we are threading, otherwise process *all* uris here.
    unthreaded_work_queue = [uri for uri in config.subscriptions() if not int(config.spider_threads()) or not _is_http_uri(uri)]
    for feed in unthreaded_work_queue:
        try:
            spiderFeed(feed, only_if_new=only_if_new)
        except Exception,e:
            import sys, traceback
            type, value, tb = sys.exc_info()
            log.error('Error processing %s', feed)
            for line in (traceback.format_exception_only(type, value) +
                traceback.format_tb(tb)):
                log.error(line.rstrip())



