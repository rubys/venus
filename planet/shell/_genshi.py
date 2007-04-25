from StringIO import StringIO
from xml.sax.saxutils import escape

from genshi.input import HTMLParser, XMLParser
from genshi.template import Context, MarkupTemplate

subscriptions = []
feed_types = [
    'application/atom+xml',
    'application/rss+xml',
    'application/rdf+xml'
]

def norm(value):
    """ Convert to Unicode """
    if hasattr(value,'items'):
        return dict([(norm(n),norm(v)) for n,v in value.items()])

    try:
        return value.decode('utf-8')
    except:
        return value.decode('iso-8859-1')

def find_config(config, feed):
    # match based on self link
    for link in feed.links:
        if link.has_key('rel') and link.rel=='self':
            if link.has_key('type') and link.type in feed_types:
                if link.has_key('href') and link.href in subscriptions:
                    return norm(dict(config.parser.items(link.href)))

    # match based on name
    for sub in subscriptions:
        if config.parser.has_option(sub, 'name') and \
            norm(config.parser.get(sub, 'name')) == feed.planet_name:
            return norm(dict(config.parser.items(sub)))

    return {}

class XHTMLParser(object):
    """ parse an XHTML fragment """
    def __init__(self, text):
        self.parser = XMLParser(StringIO("<div>%s</div>" % text))
        self.depth = 0
    def __iter__(self):
        self.iter = self.parser.__iter__()
        return self
    def next(self):
        object = self.iter.next()
        if object[0] == 'END': self.depth = self.depth - 1
        predepth = self.depth
        if object[0] == 'START': self.depth = self.depth + 1
        if predepth: return object
        return self.next()

def streamify(text,bozo):
    """ add a .stream to a _detail textConstruct """
    if text.type == 'text/plain':
        text.stream = HTMLParser(StringIO(escape(text.value)))
    elif text.type == 'text/html' or bozo != 'false':
        text.stream = HTMLParser(StringIO(text.value))
    else:
        text.stream = XHTMLParser(text.value)

def run(script, doc, output_file=None, options={}):
    """ process an Genshi template """

    context = Context(**options)

    tmpl_fileobj = open(script)
    tmpl = MarkupTemplate(tmpl_fileobj, script)
    tmpl_fileobj.close()

    if not output_file: 
        # filter
        context.push({'input':XMLParser(StringIO(doc))})
    else:
        # template
        import time
        from planet import config,feedparser
        from planet.spider import filename

        # gather a list of subscriptions, feeds
        global subscriptions
        feeds = []
        sources = config.cache_sources_directory()
        for sub in config.subscriptions():
            data=feedparser.parse(filename(sources,sub))
            data.feed.config = norm(dict(config.parser.items(sub)))
            if data.feed.has_key('link'):
                feeds.append((data.feed.config.get('name',''),data.feed))
            subscriptions.append(norm(sub))
        feeds.sort()

        # annotate each entry
        new_date_format = config.new_date_format()
        vars = feedparser.parse(StringIO(doc))
        vars.feeds = [value for name,value in feeds]
        last_feed = None
        last_date = None
        for entry in vars.entries:
             entry.source.config = find_config(config, entry.source)

             # add new_feed and new_date fields
             entry.new_feed = entry.source.id
             entry.new_date = date = None
             if entry.has_key('published_parsed'): date=entry.published_parsed
             if entry.has_key('updated_parsed'): date=entry.updated_parsed
             if date: entry.new_date = time.strftime(new_date_format, date)

             # remove new_feed and new_date fields if not "new"
             if entry.new_date == last_date:
                 entry.new_date = None
                 if entry.new_feed == last_feed:
                     entry.new_feed = None
                 else:
                     last_feed = entry.new_feed
             elif entry.new_date:
                 last_date = entry.new_date
                 last_feed = None

             # add streams for all text constructs
             for key in entry.keys():
                 if key.endswith("_detail") and entry[key].has_key('type') and \
                     entry[key].has_key('value'):
                     streamify(entry[key],entry.source.planet_bozo)
             if entry.has_key('content'):
                 for content in entry.content:
                     streamify(content,entry.source.planet_bozo)
     
        # add cumulative feed information to the Genshi context
        vars.feed.config = dict(config.parser.items('Planet',True))
        context.push(vars)

    # apply template
    output=tmpl.generate(context).render('xml')

    if output_file:
        out_file = open(output_file,'w')
        out_file.write(output)
        out_file.close()
    else:
        return output
