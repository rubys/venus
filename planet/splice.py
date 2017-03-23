# coding=utf-8
""" Splice together a planet from a cache of feed entries """
import glob
import os
import shutil
import sys
import time
import traceback
from xml.dom import minidom

import feedparser

import config
import planet
import reconstitute
import shell
from planet import idindex, logger
from reconstitute import createTextElement, date
from spider import filename


def splice():
    """ Splice together a planet from a cache of entries """

    logger.info("Loading cached data")
    cache = config.cache_directory()
    dir_ = [(os.stat(filepath).st_mtime, filepath) for filepath in glob.glob(cache + "/*") if not os.path.isdir(filepath)]
    dir_.sort()
    dir_.reverse()

    max_items = max([config.items_per_page(templ) for templ in config.template_files() or ['Planet']])

    doc = minidom.parseString('<feed xmlns="http://www.w3.org/2005/Atom"/>')
    feed = doc.documentElement

    # insert feed information
    createTextElement(feed, 'title', config.name())
    date(feed, 'updated', time.gmtime())
    gen = createTextElement(feed, 'generator', config.generator())
    gen.setAttribute('uri', config.generator_uri())

    author = doc.createElement('author')
    createTextElement(author, 'name', config.owner_name())
    createTextElement(author, 'email', config.owner_email())
    feed.appendChild(author)

    if config.feed():
        createTextElement(feed, 'id', config.feed())
        link = doc.createElement('link')
        link.setAttribute('rel', 'self')
        link.setAttribute('href', config.feed())
        if config.feedtype():
            link.setAttribute('type', "application/%s+xml" % config.feedtype())
        feed.appendChild(link)

    if config.pubsubhubbub_hub():
        hub = doc.createElement('link')
        hub.setAttribute('rel', 'hub')
        hub.setAttribute('href', config.pubsubhubbub_hub())
        feed.appendChild(hub)

    if config.link():
        link = doc.createElement('link')
        link.setAttribute('rel', 'alternate')
        link.setAttribute('href', config.link())
        feed.appendChild(link)

    # insert subscription information
    sub_ids = []
    feed.setAttribute('xmlns:planet', planet.xmlns)
    sources = config.cache_sources_directory()
    for sub in config.subscriptions():
        data = feedparser.parse(filename(sources, sub))
        if 'id' in data.feed.keys():
            sub_ids.append(data.feed.id)
        if not data.feed:
            continue

        # warn on missing links
        if 'planet_message' not in data.feed.keys():
            if 'links' not in data.feed.keys():
                data.feed['links'] = []

            for link in data.feed.links:
                if link.rel == 'self':
                    break
            else:
                logger.debug('missing self link for ' + sub)

            for link in data.feed.links:
                if link.rel == 'alternate' and 'html' in link.type:
                    break
            else:
                logger.debug('missing html link for ' + sub)

        xdoc = minidom.parseString('''<planet:source xmlns:planet="%s"
             xmlns="http://www.w3.org/2005/Atom"/>\n''' % planet.xmlns)
        reconstitute.source(xdoc.documentElement, data.feed, None, None)
        feed.appendChild(xdoc.documentElement)

    index = idindex.open()

    # insert entry information
    items = 0
    count = {}
    atomNS = 'http://www.w3.org/2005/Atom'
    new_feed_items = config.new_feed_items()
    for mtime, filepath in dir_:
        if index is not None:
            base = os.path.basename(filepath)
            if base in index.keys() and index[base] not in sub_ids:
                continue

        try:
            entry = minidom.parse(filepath)

            # verify that this entry is currently subscribed to and that the
            # number of entries contributed by this feed does not exceed
            # config.new_feed_items
            entry.normalize()
            sources = entry.getElementsByTagNameNS(atomNS, 'source')
            if sources:
                ids = sources[0].getElementsByTagName('id')
                if ids:
                    id_ = ids[0].childNodes[0].nodeValue
                    count[id_] = count.get(id_, 0) + 1
                    if new_feed_items and count[id_] > new_feed_items:
                        continue

                    if id_ not in sub_ids:
                        ids = sources[0].getElementsByTagName('planet:id')
                        if not ids:
                            continue
                        id_ = ids[0].childNodes[0].nodeValue
                        if id_ not in sub_ids:
                            logger.warn('Skipping: ' + id_)
                        if id_ not in sub_ids:
                            continue

            # add entry to feed
            feed.appendChild(entry.documentElement)
            items = items + 1
            if items >= max_items:
                break
        except Exception as e:
            print("WARNING: Broad exception caught. FIXME")
            print(e)
            print(traceback.print_exception(*sys.exc_info()))
            logger.error("Error parsing %s", filepath)

    if index:
        index.close()

    return doc


def apply(doc):
    output_dir = config.output_dir()
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    planet_filters = config.filters('Planet')

    # Go-go-gadget-template
    for template_file in config.template_files():
        output_file = shell.run(template_file, doc)

        # run any template specific filters
        if config.filters(template_file) != planet_filters:
            with open(output_file) as fp:
                output = fp.read()
            for filter_ in config.filters(template_file):
                if filter_ in planet_filters:
                    continue
                if filter_.find('>') > 0:
                    # tee'd output
                    filter_, dest = filter_.split('>', 1)
                    tee = shell.run(filter_.strip(), output, mode="filter")
                    if tee:
                        output_dir = planet.config.output_dir()
                        dest_file = os.path.join(output_dir, dest.strip())
                        with open(dest_file, 'w') as outputfile:
                            outputfile.write(tee)
                else:
                    # pipe'd output
                    output = shell.run(filter_, output, mode="filter")
                    if not output:
                        os.unlink(output_file)
                        break
            else:
                with open(output_file, 'w') as handle:
                    handle.write(output)

    # Process bill of materials
    for copy_file in config.bill_of_materials():
        dest = os.path.join(output_dir, copy_file)
        for template_dir in config.template_directories():
            source = os.path.join(template_dir, copy_file)
            if os.path.exists(source):
                break
        else:
            logger.error('Unable to locate %s', copy_file)
            logger.info("Template search path:")
            for template_dir in config.template_directories():
                logger.info("    %s", os.path.realpath(template_dir))
            continue

        mtime = os.stat(source).st_mtime
        if not os.path.exists(dest) or os.stat(dest).st_mtime < mtime:
            dest_dir = os.path.split(dest)[0]
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

            logger.info("Copying %s to %s", source, dest)
            if os.path.exists(dest):
                os.chmod(dest, 0o644)
            shutil.copyfile(source, dest)
            shutil.copystat(source, dest)
