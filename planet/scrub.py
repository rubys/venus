# coding=utf-8
"""
Process a set of configuration defined sanitations on a given feed.
"""

# Standard library modules
import sys
import time
import traceback

from html5lib import html5parser, sanitizer, serializer, treebuilders, treewalkers

# Planet modules
import config
from planet import feedparser
from shell.tmpl import stripHtml

type_map = {'text': 'text/plain',
            'html': 'text/html',
            'xhtml': 'application/xhtml+xml'}


def scrub(feed_uri, data):
    # some data is not trustworthy
    for tag in config.ignore_in_feed(feed_uri).split():
        if tag.find('lang') >= 0:
            tag = 'language'
        if tag in data.feed.keys():
            del data.feed[tag]
        for entry in data.entries:
            if tag in entry.keys():
                del entry[tag]
            if tag + "_detail" in entry.keys():
                del entry[tag + "_detail"]
            if tag + "_parsed" in entry.keys():
                del entry[tag + "_parsed"]
            for key in entry.keys():
                if not key.endswith('_detail'):
                    continue
                for detail in entry[key].copy():
                    if detail == tag:
                        del entry[key][detail]

    # adjust title types
    if config.title_type(feed_uri):
        title_type = config.title_type(feed_uri)
        title_type = type_map.get(title_type, title_type)
        for entry in data.entries:
            if 'title_detail' in entry.keys():
                entry.title_detail['type'] = title_type

    # adjust summary types
    if config.summary_type(feed_uri):
        summary_type = config.summary_type(feed_uri)
        summary_type = type_map.get(summary_type, summary_type)
        for entry in data.entries:
            if 'summary_detail' in entry.keys():
                entry.summary_detail['type'] = summary_type

    # adjust content types
    if config.content_type(feed_uri):
        content_type = config.content_type(feed_uri)
        content_type = type_map.get(content_type, content_type)
        for entry in data.entries:
            if 'content' in entry.keys():
                entry.content[0]['type'] = content_type

    # some people put html in author names
    if config.name_type(feed_uri).find('html') >= 0:
        if 'author_detail' in data.feed.keys() and \
                        'name' in data.feed.author_detail.keys():
            data.feed.author_detail['name'] = \
                str(stripHtml(data.feed.author_detail.name))
        for entry in data.entries:
            if 'author_detail' in entry.keys() and \
                            'name' in entry.author_detail.keys():
                entry.author_detail['name'] = \
                    str(stripHtml(entry.author_detail.name))
            if 'source' in entry.keys():
                source = entry.source
                if 'author_detail' in source.keys() and \
                                'name' in source.author_detail.keys():
                    source.author_detail['name'] = \
                        str(stripHtml(source.author_detail.name))

    # handle dates in the future
    future_dates = config.future_dates(feed_uri).lower()
    if future_dates == 'ignore_date':
        now = time.gmtime()
        if 'updated_parsed' in data.feed.keys() and data.feed['updated_parsed']:
            if data.feed['updated_parsed'] > now:
                del data.feed['updated_parsed']
        for entry in data.entries:
            if 'published_parsed' in entry.keys() and entry['published_parsed']:
                if entry['published_parsed'] > now:
                    del entry['published_parsed']
                    del entry['published']
            if 'updated_parsed' in entry.keys() and entry['updated_parsed']:
                if entry['updated_parsed'] > now:
                    del entry['updated_parsed']
                    del entry['updated']
    elif future_dates == 'ignore_entry':
        now = time.time()
        if 'updated_parsed' in data.feed.keys() and data.feed['updated_parsed']:
            if data.feed['updated_parsed'] > now:
                del data.feed['updated_parsed']
        data.entries = [entry for entry in data.entries if
                        ('published_parsed' not in entry.keys() or not entry['published_parsed']
                         or entry['published_parsed'] <= now) and
                        ('updated_parsed' not in entry.keys() or not entry['updated_parsed']
                         or entry['updated_parsed'] <= now)]

    scrub_xmlbase = config.xml_base(feed_uri)

    # resolve relative URIs and sanitize
    for entry in data.entries + [data.feed]:
        for key in entry.keys():
            if key == 'content' and 'content_detail' not in entry.keys():
                node = entry.content[0]
            elif key.endswith('_detail'):
                node = entry[key]
            else:
                continue

            if 'type' not in node.keys():
                continue
            if 'html' not in node['type']:
                continue
            if 'value' not in node.keys():
                continue

            if 'base' in node.keys():
                if scrub_xmlbase:
                    if scrub_xmlbase == 'feed_alternate':
                        if 'source' in entry.keys() and \
                                        'link' in entry.source.keys():
                            node['base'] = entry.source.link
                        elif 'link' in data.feed.keys():
                            node['base'] = data.feed.link
                    elif scrub_xmlbase == 'entry_alternate':
                        if 'link' in entry.keys():
                            node['base'] = entry.link
                    else:
                        node['base'] = feedparser._urljoin(node['base'], scrub_xmlbase)

                node['value'] = feedparser._resolveRelativeURIs(node.value, node.base, 'utf-8', node.type)

            if node['value']:
                # Run this through HTML5's sanitizer
                doc = None
                if 'xhtml' in node['type']:
                    try:
                        from xml.dom import minidom
                        doc = minidom.parseString(node['value'])
                    except Exception as e:
                        print("WARNING: Broad exception caught. FIXME")
                        print(e)
                        print(traceback.print_exception(*sys.exc_info()))
                        node['type'] = 'text/html'

                if not doc:
                    p = html5parser.HTMLParser(tree=treebuilders.getTreeBuilder('dom'), tokenizer=sanitizer.HTMLSanitizer)
                    doc = p.parseFragment(node['value'], encoding='utf-8')

                walker = treewalkers.getTreeWalker('dom')(doc)
                xhtml = serializer.HTMLSerializer(inject_meta_charset=False)
                tree = xhtml.serialize(walker, encoding='utf-8')
                node['value'] = ''.join([str(token) for token in tree])
