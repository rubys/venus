# coding=utf-8
"""
Fetch either a single feed, or a set of feeds, normalize to Atom and XHTML,
and write each as a set of entries in a cache directory.
"""

# Standard library modules
import calendar
import os
import re
import socket
import sys
import time
import traceback
import urlparse
from Queue import Queue
from StringIO import StringIO
from hashlib import md5
from httplib import BadStatusLine
from threading import Thread
from xml.dom import minidom

import feedparser
import httplib2

# Planet modules
import config
import planet
import reconstitute
import scrub
import shell

# Regular expressions to sanitise cache filenames
re_url_scheme = re.compile(r'^\w+:/*(\w+:|www\.)?')
re_slash = re.compile(r'[?/:|]+')
re_initial_cruft = re.compile(r'^[,.]*')
re_final_cruft = re.compile(r'[,.]*$')

index = True


def filename(directory, fname):
    """Return a filename suitable for the cache.

    Strips dangerous and common characters to create a filename we
    can use to store the cache in.
    """
    try:
        if re_url_scheme.match(fname):
            if isinstance(fname, str):
                fname = fname.decode('utf-8').encode('idna')
            else:
                fname = fname.encode('idna')
    except Exception as e:
        print("WARNING: Broad exception caught. FIXME")
        print(e)
        print(traceback.print_exception(*sys.exc_info()))

    if isinstance(fname, unicode):
        fname = fname.encode('utf-8')
    fname = re_url_scheme.sub("", fname)
    fname = re_slash.sub(",", fname)
    fname = re_initial_cruft.sub("", fname)
    fname = re_final_cruft.sub("", fname)

    # limit length of filename
    if len(fname) > 250:
        parts = fname.split(',')
        for i in range(len(parts), 0, -1):
            if len(','.join(parts[:i])) < 220:
                fname = ','.join(parts[:i]) + ',' + \
                        md5(','.join(parts[i:])).hexdigest()
                break

    return os.path.join(directory, fname)


def write(xdoc, out, mtime=None):
    """ write the document out to disk """
    with open(out, 'w') as output:
        output.write(xdoc)
    if mtime:
        os.utime(out, (mtime, mtime))


def _is_http_uri(uri):
    parsed = urlparse.urlparse(uri)
    return parsed[0] in ['http', 'https']


def writeCache(feed_uri, feed_info, data):
    log = planet.logger
    sources = config.cache_sources_directory()
    blacklist = config.cache_blacklist_directory()

    # capture http status
    if 'status' not in data.keys():
        if 'entries' not in data.keys() and len(data.entries) > 0:
            data.status = 200
        elif data.bozo and data.bozo_exception.__class__.__name__.lower() == 'timeout':
            data.status = 408
        else:
            data.status = 500

    activity_horizon = \
        time.gmtime(time.time() - 86400 * config.activity_threshold(feed_uri))

    # process based on the HTTP status code
    if data.status == 200 and 'url' in data.keys():
        feed_info.feed['planet_http_location'] = data.url
        if 'entries' in data.keys() and len(data.entries) == 0:
            log.warning("No data %s", feed_uri)
            feed_info.feed['planet_message'] = 'no data'
        elif feed_uri == data.url:
            log.info("Updating feed %s", feed_uri)
        else:
            log.info("Updating feed %s @ %s", feed_uri, data.url)
    elif data.status == 301 and 'entries' in data.keys() and len(data.entries) > 0:
        log.warning("Feed has moved from <%s> to <%s>", feed_uri, data.url)
        data.feed['planet_http_location'] = data.url
    elif data.status == 304 and 'url' in data.keys():
        feed_info.feed['planet_http_location'] = data.url
        if feed_uri == data.url:
            log.info("Feed %s unchanged", feed_uri)
        else:
            log.info("Feed %s unchanged @ %s", feed_uri, data.url)

        if 'planet_message' not in feed_info.feed.keys():
            if 'planet_updated' in feed_info.feed.keys():
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
        data.bozo = feed_info.feed.get('planet_bozo', 'true') == 'true'
        data.version = feed_info.feed.get('planet_format')
    data.feed['planet_http_status'] = str(data.status)

    # capture etag and last-modified information
    if 'headers' in data.keys():
        if 'etag' in data.keys() and data.etag:
            data.feed['planet_http_etag'] = data.etag
        elif 'etag' in data.headers.keys() and data.headers['etag']:
            data.feed['planet_http_etag'] = data.headers['etag']

        if 'last-modified' in data.headers.keys():
            data.feed['planet_http_last_modified'] = data.headers['last-modified']
        elif 'modified' in data.keys() and data.modified:
            data.feed['planet_http_last_modified'] = time.asctime(data.modified)

        if '-content-hash' in data.headers.keys():
            data.feed['planet_content_hash'] = data.headers['-content-hash']

    # capture feed and data from the planet configuration file
    if data.get('version'):
        if 'links' not in data.keys():
            data.feed['links'] = list()
        feedtype = 'application/atom+xml'
        if data.version.startswith('rss'):
            feedtype = 'application/rss+xml'
        if data.version in ['rss090', 'rss10']:
            feedtype = 'application/rdf+xml'
        for link in data.feed.links:
            if link.rel == 'self':
                link['type'] = feedtype
                break
        else:
            data.feed.links.append(feedparser.FeedParserDict({'rel': 'self', 'type': feedtype, 'href': feed_uri}))
    for name, value in config.feed_options(feed_uri).items():
        data.feed['planet_' + name] = value

    # perform user configured scrub operations on the data
    scrub.scrub(feed_uri, data)

    from planet import idindex
    global index
    if index is not None:
        index = idindex.open()

    # select latest entry for each unique id
    ids = {}
    for entry in data.entries:
        # generate an id, if none is present
        if 'id' not in entry.keys() or not entry.id:
            entry['id'] = reconstitute.id(None, entry)
        elif hasattr(entry['id'], 'values'):
            entry['id'] = entry['id'].values()[0]
        if not entry['id']:
            continue

        # determine updated date for purposes of selection
        updated = ''
        if 'published' in entry.keys():
            updated = entry.published
        if 'updated' in entry.keys():
            updated = entry.updated

        # if not seen or newer than last seen, select it
        if updated >= ids.get(entry.id, ('',))[0]:
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
        if 'updated_parsed' not in entry.keys() or not entry['updated_parsed']:
            entry['updated_parsed'] = entry.get('published_parsed', None)
        if 'updated_parsed' in entry.keys():
            try:
                mtime = calendar.timegm(entry.updated_parsed)
            except Exception as e:
                print("WARNING: Broad exception caught. FIXME")
                print(e)
                print(traceback.print_exception(*sys.exc_info()))
        if not mtime:
            try:
                mtime = os.stat(cache_file).st_mtime
            except Exception as e:
                print(e)
                if 'updated_parsed' in data.feed.keys():
                    try:
                        mtime = calendar.timegm(data.feed.updated_parsed)
                    except Exception as e:
                        print("WARNING: Broad exception caught. FIXME")
                        print(e)
                        print(traceback.print_exception(*sys.exc_info()))
        if not mtime:
            mtime = time.time()
        entry['updated_parsed'] = time.gmtime(mtime)

        # apply any filters
        xdoc = reconstitute.reconstitute(data, entry)
        output = xdoc.toxml().encode('utf-8')
        xdoc.unlink()
        for filter_ in config.filters(feed_uri):
            output = shell.run(filter_, output, mode="filter")
            if not output:
                break
        if not output:
            if os.path.exists(cache_file):
                os.remove(cache_file)
            continue

        # write out and timestamp the results
        write(output, cache_file, mtime)

        # optionally index
        if index is not None:
            feedid = data.feed.get('id', data.feed.get('link', None))
            if feedid:
                if type(feedid) == unicode:
                    feedid = feedid.encode('utf-8')
                index[filename('', entry.id)] = feedid

    if index:
        index.close()

    # identify inactive feeds
    if config.activity_threshold(feed_uri):
        updated = [entry.updated_parsed for entry in data.entries
                   if 'updated_parsed' in entry.keys()]
        updated.sort()

        if updated:
            data.feed['planet_updated'] = \
                time.strftime("%Y-%m-%dT%H:%M:%SZ", updated[-1])
        elif 'planet_updated' in data.feed.keys():
            updated = [feedparser._parse_date_iso8601(data.feed.planet_updated)]

        if not updated or updated[-1] < activity_horizon:
            msg = "no activity in %d days" % config.activity_threshold(feed_uri)
            log.info(msg)
            data.feed['planet_message'] = msg

    # report channel level errors
    if data.status == 226:
        if 'planet_message' in data.feed.keys():
            del data.feed['planet_message']
        if 'planet_updated' in feed_info.feed.keys():
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
    if not os.path.exists(sources):
        os.makedirs(sources)
    xdoc = minidom.parseString('''<feed xmlns:planet="%s"
      xmlns="http://www.w3.org/2005/Atom"/>\n''' % planet.xmlns)
    reconstitute.source(xdoc.documentElement, data.feed, data.bozo, data.version)
    write(xdoc.toxml().encode('utf-8'), filename(sources, feed_uri))
    xdoc.unlink()


def httpThread(thread_index, input_queue, output_queue, log):
    h = httplib2.Http(config.http_cache_directory())
    uri, feed_info = input_queue.get(block=True)
    while uri:
        log.info("Fetching %s via %d", uri, thread_index)
        feed = StringIO('')
        setattr(feed, 'url', uri)
        setattr(feed, 'headers',
                feedparser.FeedParserDict({'status': '500'}))
        try:
            # map IRI => URI
            try:
                if isinstance(uri, unicode):
                    idna = uri.encode('idna')
                else:
                    idna = uri.decode('utf-8').encode('idna')
                if idna != uri:
                    log.info("IRI %s mapped to %s", uri, idna)
            except Exception as e:
                print("WARNING: Broad exception caught. FIXME")
                print(e)
                print(traceback.print_exception(*sys.exc_info()))
                log.info("unable to map %s to a URI", uri)
                idna = uri

            # cache control headers
            headers = {}
            if 'planet_http_etag' in feed_info.feed.keys():
                headers['If-None-Match'] = feed_info.feed['planet_http_etag']
            if 'planet_http_last_modified' in feed_info.feed.keys():
                headers['If-Modified-Since'] = \
                    feed_info.feed['planet_http_last_modified']

            # issue request
            (resp, content) = h.request(idna, 'GET', headers=headers)

            # unchanged detection
            resp['-content-hash'] = md5(content or '').hexdigest()
            if resp.status == 200:
                if resp.fromcache:
                    resp.status = 304
                elif 'planet_content_hash' in feed_info.feed.keys() and \
                                feed_info.feed['planet_content_hash'] == resp['-content-hash']:
                    resp.status = 304

            # build a file-like object
            feed = StringIO(content)
            setattr(feed, 'url', resp.get('content-location', uri))
            if 'content-encoding' in resp.keys():
                del resp['content-encoding']
            setattr(feed, 'headers', resp)
        except BadStatusLine:
            log.error("Bad Status Line received for %s via %d",
                      uri, thread_index)
        except httplib2.HttpLib2Error as e:
            log.error("HttpLib2Error: %s via %d", str(e), thread_index)
        except socket.error as e:
            if e.__class__.__name__.lower() == 'timeout':
                feed.headers['status'] = '408'
                log.warn("Timeout in thread-%d", thread_index)
            else:
                log.error("HTTP Error: %s in thread-%d", str(e), thread_index)
        except Exception as e:
            print("WARNING: Broad exception caught. FIXME")
            print(e)
            print(traceback.print_exception(*sys.exc_info()))
            type_, value, tb = sys.exc_info()
            log.error('Error processing %s', uri)
            for line in (traceback.format_exception_only(type_, value) + traceback.format_tb(tb)):
                log.error(line.rstrip())

        output_queue.put(block=True, item=(uri, feed_info, feed))
        uri, feed_info = input_queue.get(block=True)


def spiderPlanet(only_if_new=False):
    """ Spider (fetch) an entire planet """
    log = planet.logger

    global index
    index = True

    timeout = config.feed_timeout()
    socket.setdefaulttimeout(float(timeout))
    log.info("Socket timeout set to %d seconds", timeout)

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
                                args=(i, fetch_queue, parse_queue, log))
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
        if feed_info.feed.get('planet_http_status', None) == '410':
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

                if not hasattr(feed, 'headers') or int(feed.headers.status) < 300:
                    options = {}
                    if hasattr(feed_info, 'feed'):
                        options['etag'] = \
                            feed_info.feed.get('planet_http_etag', None)
                        try:
                            # TODO This just silently fails everytime since strptime is not provided a format
                            modified = time.strptime(feed_info.feed.get('planet_http_last_modified', None))
                        except Exception as e:
                            print("WARNING: Broad exception caught. FIXME")
                            print(e)
                            print(traceback.print_exception(*sys.exc_info()))

                    data = feedparser.parse(feed, **options)
                else:
                    data = feedparser.FeedParserDict({'version': None,
                                                      'headers': feed.headers, 'entries': [], 'feed': {},
                                                      'href': feed.url, 'bozo': 0,
                                                      'status': int(feed.headers.status)})

                # duplicate feed?
                id_ = data.feed.get('id', None)
                if not id_:
                    id_ = feed_info.feed.get('id', None)

                href = uri
                if 'href' in data.keys():
                    href = data.href

                duplicate = None
                if id_ and id_ in feeds_seen:
                    duplicate = id_
                elif href and href in feeds_seen:
                    duplicate = href

                if duplicate:
                    feed_info.feed['planet_message'] = 'duplicate subscription: ' + feeds_seen[duplicate]
                    log.warn('Duplicate subscription: %s and %s' % (uri, feeds_seen[duplicate]))
                    if href:
                        feed_info.feed['planet_http_location'] = href

                if id_:
                    feeds_seen[id_] = uri
                if href:
                    feeds_seen[href] = uri

                # complete processing for the feed
                writeCache(uri, feed_info, data)

            except Exception as e:
                print("WARNING: Broad exception caught. FIXME")
                print(e)
                print(traceback.print_exception(*sys.exc_info()))
                type_, value, tb = sys.exc_info()
                log.error('Error processing %s', uri)
                for line in (traceback.format_exception_only(type_, value) + traceback.format_tb(tb)):
                    log.error(line.rstrip())

        time.sleep(0.1)

        for index in threads.keys():
            if not threads[index].isAlive():
                del threads[index]
                if not threads:
                    log.info("Finished threaded part of processing.")
