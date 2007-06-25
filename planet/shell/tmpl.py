from xml.sax.saxutils import escape
import sgmllib, time, os, sys, new, urlparse, re
from planet import config, feedparser
import htmltmpl

voids=feedparser._BaseHTMLProcessor.elements_no_end_tag
empty=re.compile(r"<((%s)[^>]*)></\2>" % '|'.join(voids))

class stripHtml(sgmllib.SGMLParser):
    "remove all tags from the data"
    def __init__(self, data):
        sgmllib.SGMLParser.__init__(self)
        self.result=''
        if isinstance(data, str):
            try:
                self.feed(data.decode('utf-8'))
            except:
                self.feed(data)
        else:
            self.feed(data)
        self.close()
    def __str__(self):
        if isinstance(self.result, unicode):
            return self.result.encode('utf-8')
        return self.result
    def handle_entityref(self, ref):
        import htmlentitydefs
        if ref in htmlentitydefs.entitydefs:
            ref=htmlentitydefs.entitydefs[ref]
            if len(ref)==1:
                self.result+=unichr(ord(ref))
            elif ref.startswith('&#') and ref.endswith(';'):
                self.handle_charref(ref[2:-1])
            else:
                self.result+='&%s;' % ref
        else:
            self.result+='&%s;' % ref
    def handle_charref(self, ref):
        try:
            if ref.startswith('x'):
                self.result+=unichr(int(ref[1:],16))
            else:
                self.result+=unichr(int(ref))
        except:
            self.result+='&#%s;' % ref
    def handle_data(self, data):
        if data: self.result+=data

# Data format mappers

def String(value):
    if isinstance(value, unicode): return value.encode('utf-8')
    return value

def Plain(value):
    return str(stripHtml(value))

def PlanetDate(value):
    return time.strftime(config.date_format(), value)

def NewDate(value):
    return time.strftime(config.new_date_format(), value)

def Rfc822(value):
    return time.strftime("%a, %d %b %Y %H:%M:%S +0000", value)

def Rfc3399(value):
    return time.strftime("%Y-%m-%dT%H:%M:%S+00:00", value)

# Map from FeedParser path to Planet tmpl names
Base = [
    ['author', String, 'author'],
    ['author_name', String, 'author_detail', 'name'],
    ['generator', String, 'generator'],
    ['id', String, 'id'],
    ['icon', String, 'icon'],
    ['last_updated_822', Rfc822, 'updated_parsed'],
    ['last_updated_iso', Rfc3399, 'updated_parsed'],
    ['last_updated', PlanetDate, 'updated_parsed'],
    ['link', String, 'link'],
    ['logo', String, 'logo'],
    ['rights', String, 'rights_detail', 'value'],
    ['subtitle', String, 'subtitle_detail', 'value'],
    ['title', String, 'title_detail', 'value'],
    ['title_plain', Plain, 'title_detail', 'value'],
    ['url', String, 'links', {'rel':'self'}, 'href'],
    ['url', String, 'planet_http_location'],
]

Items = [
    ['author', String, 'author'],
    ['author_email', String, 'author_detail', 'email'],
    ['author_name', String, 'author_detail', 'name'],
    ['author_uri', String, 'author_detail', 'href'],
    ['content_language', String, 'content', 0, 'language'],
    ['content', String, 'summary_detail', 'value'],
    ['content', String, 'content', 0, 'value'],
    ['date', PlanetDate, 'published_parsed'],
    ['date', PlanetDate, 'updated_parsed'],
    ['date_822', Rfc822, 'published_parsed'],
    ['date_822', Rfc822, 'updated_parsed'],
    ['date_iso', Rfc3399, 'published_parsed'],
    ['date_iso', Rfc3399, 'updated_parsed'],
    ['enclosure_href', String, 'links', {'rel': 'enclosure'}, 'href'],
    ['enclosure_length', String, 'links', {'rel': 'enclosure'}, 'length'],
    ['enclosure_type', String, 'links', {'rel': 'enclosure'}, 'type'],
    ['id', String, 'id'],
    ['link', String, 'links', {'rel': 'alternate'}, 'href'],
    ['new_channel', String, 'source', 'id'],
    ['new_date', NewDate, 'published_parsed'],
    ['new_date', NewDate, 'updated_parsed'],
    ['rights', String, 'rights_detail', 'value'],
    ['title_language', String, 'title_detail', 'language'],
    ['title_plain', Plain, 'title_detail', 'value'],
    ['title', String, 'title_detail', 'value'],
    ['summary_language', String, 'summary_detail', 'language'],
    ['updated', PlanetDate, 'updated_parsed'],
    ['updated_822', Rfc822, 'updated_parsed'],
    ['updated_iso', Rfc3399, 'updated_parsed'],
    ['published', PlanetDate, 'published_parsed'],
    ['published_822', Rfc822, 'published_parsed'],
    ['published_iso', Rfc3399, 'published_parsed'],
]

# Add additional rules for source information
for rule in Base:
    Items.append(['channel_'+rule[0], rule[1], 'source'] + rule[2:])

def tmpl_mapper(source, rules):
    "Apply specified rules to the source, and return a template dictionary"
    output = {}

    for rule in rules:
        node = source
        for path in rule[2:]:
            if isinstance(path, str) and path in node:
                if path == 'value':
                    if node.get('type','')=='text/plain':
                        node['value'] = escape(node['value'])
                        node['type'] = 'text/html'
                    elif node.get('type','')=='application/xhtml+xml':
                        node['value'] = empty.sub(r"<\1 />", node['value'])
                node = node[path]
            elif isinstance(path, int):
                node = node[path]
            elif isinstance(path, dict):
                for test in node:
                    for key, value in path.items():
                        if test.get(key,None) != value: break
                    else:
                        node = test
                        break
                else:
                    break
            else:
                break
        else:
            if node: output[rule[0]] = rule[1](node)
        
    # copy over all planet namespaced elements from parent source
    for name,value in source.items():
        if name.startswith('planet_'):
            output[name[7:]] = String(value)

    # copy over all planet namespaced elements from child source element
    if 'source' in source:
        for name,value in source.source.items():
            if name.startswith('planet_'):
                output['channel_' + name[7:]] = String(value)

    return output

def _end_planet_source(self):
    self._end_source()
    context = self._getContext()
    if not context.has_key('sources'): context['sources'] = []
    context.sources.append(context.source)
    del context['source']

def template_info(source):
    """ get template information from a feedparser output """

    # wire in support for planet:source, call feedparser, unplug planet:source
    mixin=feedparser._FeedParserMixin
    mixin._start_planet_source = mixin._start_source
    mixin._end_planet_source = \
        new.instancemethod(_end_planet_source, None, mixin)
    data=feedparser.parse(source)
    del mixin._start_planet_source
    del mixin._end_planet_source

    # apply rules to convert feed parser output to htmltmpl input
    output = {'Channels': [], 'Items': []}
    output.update(tmpl_mapper(data.feed, Base))
    sources = [(source.get('planet_name',None),source)
        for source in data.feed.get('sources',[])]
    sources.sort()
    for name, feed in sources:
        output['Channels'].append(tmpl_mapper(feed, Base))
    for entry in data.entries:
        output['Items'].append(tmpl_mapper(entry, Items))

    # synthesize isPermaLink attribute
    for item in output['Items']:
        if item.get('id') == item.get('link'):
            item['guid_isPermaLink']='true'
        else:
            item['guid_isPermaLink']='false'

    # feed level information
    output['generator'] = config.generator_uri()
    output['name'] = config.name()
    output['link'] = config.link()
    output['owner_name'] = config.owner_name()
    output['owner_email'] = config.owner_email()
    if config.feed():
        output['feed'] = config.feed()
        output['feedtype'] = config.feed().find('rss')>=0 and 'rss' or 'atom'

    # date/time information
    date = time.gmtime()
    output['date'] = PlanetDate(date)
    output['date_iso'] = Rfc3399(date)
    output['date_822'] = Rfc822(date)

    # remove new_dates and new_channels that aren't "new"
    date = channel = None
    for item in output['Items']:
        if item.has_key('new_date'):
            if item['new_date'] == date:
                del item['new_date']
            else:
                date = item['new_date']

        if item.has_key('new_channel'):
            if item['new_channel'] == channel and not item.has_key('new_date'):
                del item['new_channel']
            else:
                channel = item['new_channel']

    return output

def run(script, doc, output_file=None, options={}):
    """ process an HTMLTMPL file """
    manager = htmltmpl.TemplateManager()
    template = manager.prepare(script)
    tp = htmltmpl.TemplateProcessor(html_escape=0)
    for key,value in template_info(doc).items():
        tp.set(key, value)

    if output_file:
        reluri = os.path.splitext(os.path.basename(output_file))[0]
        tp.set('url', urlparse.urljoin(config.link(),reluri))

        output = open(output_file, "w")
        output.write(tp.process(template))
        output.close()
    else:
        return tp.process(template)

if __name__ == '__main__':
    sys.path.insert(0, os.path.split(sys.path[0])[0])

    for test in sys.argv[1:]:
        from pprint import pprint
        pprint(template_info('/home/rubys/bzr/venus/tests/data/filter/tmpl/'+test))

