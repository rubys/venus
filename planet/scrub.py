"""
Process a set of configuration defined sanitations on a given feed.
"""

# Standard library modules
import time
# Planet modules
import planet, config, shell
from planet import feedparser

type_map = {'text': 'text/plain', 'html': 'text/html',
    'xhtml': 'application/xhtml+xml'}

def scrub(feed_uri, data):

    # some data is not trustworthy
    for tag in config.ignore_in_feed(feed_uri).split():
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
    if config.title_type(feed_uri):
        title_type = config.title_type(feed_uri)
        title_type = type_map.get(title_type, title_type)
        for entry in data.entries:
            if entry.has_key('title_detail'):
                entry.title_detail['type'] = title_type

    # adjust summary types
    if config.summary_type(feed_uri):
        summary_type = config.summary_type(feed_uri)
        summary_type = type_map.get(summary_type, summary_type)
        for entry in data.entries:
            if entry.has_key('summary_detail'):
                entry.summary_detail['type'] = summary_type

    # adjust content types
    if config.content_type(feed_uri):
        content_type = config.content_type(feed_uri)
        content_type = type_map.get(content_type, content_type)
        for entry in data.entries:
            if entry.has_key('content'):
                entry.content[0]['type'] = content_type

    # some people put html in author names
    if config.name_type(feed_uri).find('html')>=0:
        from shell.tmpl import stripHtml
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

    # handle dates in the future
    future_dates = config.future_dates(feed_uri).lower()
    if future_dates == 'ignore_date':
      now = time.gmtime()
      if data.feed.has_key('updated_parsed') and data.feed['updated_parsed']:
        if data.feed['updated_parsed'] > now: del data.feed['updated_parsed']
      for entry in data.entries:
        if entry.has_key('published_parsed') and entry['published_parsed']:
          if entry['published_parsed'] > now:
            del entry['published_parsed']
            del entry['published']
        if entry.has_key('updated_parsed') and entry['updated_parsed']:
          if entry['updated_parsed'] > now:
            del entry['updated_parsed']
            del entry['updated']
    elif future_dates == 'ignore_entry':
      now = time.time()
      if data.feed.has_key('updated_parsed') and data.feed['updated_parsed']:
        if data.feed['updated_parsed'] > now: del data.feed['updated_parsed']
      data.entries = [entry for entry in data.entries if 
        (not entry.has_key('published_parsed') or not entry['published_parsed']
          or entry['published_parsed'] <= now) and
        (not entry.has_key('updated_parsed') or not entry['updated_parsed']
          or entry['updated_parsed'] <= now)]

    scrub_xmlbase = config.xml_base(feed_uri)

    # resolve relative URIs and sanitize
    for entry in data.entries + [data.feed]:
        for key in entry.keys():
            if key == 'content'and not entry.has_key('content_detail'):
                node = entry.content[0]
            elif key.endswith('_detail'):
                node = entry[key]
            else:
                continue

            if not node.has_key('type'): continue
            if not 'html' in node['type']: continue
            if not node.has_key('value'): continue

            if node.has_key('base'):
                if scrub_xmlbase:
                    if scrub_xmlbase == 'feed_alternate':
                        if entry.has_key('source') and \
                            entry.source.has_key('link'):
                            node['base'] = entry.source.link
                        elif data.feed.has_key('link'):
                            node['base'] = data.feed.link
                    elif scrub_xmlbase == 'entry_alternate':
                        if entry.has_key('link'):
                            node['base'] = entry.link
                    else:
                        node['base'] = feedparser._urljoin(
                            node['base'], scrub_xmlbase)

                node['value'] = feedparser._resolveRelativeURIs(
                    node.value, node.base, 'utf-8', node.type)

            # Run this through HTML5's sanitizer
            doc = None
            if 'xhtml' in node['type']:
              try:
                from xml.dom import minidom
                doc = minidom.parseString(node['value'])
              except:
                node['type']='text/html'

            if not doc:
              from html5lib import html5parser, treebuilders
              p=html5parser.HTMLParser(tree=treebuilders.getTreeBuilder('dom'))
              doc = p.parseFragment(node['value'], encoding='utf-8')

            from html5lib import treewalkers, serializer
            from html5lib.filters import sanitizer
            walker = sanitizer.Filter(treewalkers.getTreeWalker('dom')(doc))
            xhtml = serializer.XHTMLSerializer(inject_meta_charset = False)
            tree = xhtml.serialize(walker, encoding='utf-8')

            node['value'] = ''.join([str(token) for token in tree])
