# coding=utf-8
import re
import sys
import traceback
import urllib
from ConfigParser import ConfigParser
from cStringIO import StringIO
from htmlentitydefs import entitydefs
from sgmllib import SGMLParser
from xml.sax import ContentHandler, SAXParseException, make_parser
from xml.sax.xmlreader import InputSource

try:
    unichr
    chr = unichr # Python2
except NameError:
    pass # Python3



# input = opml, output = ConfigParser
def opml2config(opml_input, config_=None):
    if hasattr(opml_input, 'read'):
        opml_input = opml_input.read()

    if not config_:
        config_ = ConfigParser()

    opml_parser = OpmlParser(config_)

    try:
        # try SAX
        source = InputSource()
        source.setByteStream(StringIO(opml_input))
        parser = make_parser()
        parser.setContentHandler(opml_parser)
        parser.parse(source)
    except SAXParseException:
        # try as SGML
        opml_parser.feed(opml_input)

    return config_


# Parse OPML via either SAX or SGML
class OpmlParser(ContentHandler, SGMLParser):
    entities = re.compile('&(#?\w+);')

    def __init__(self, config_):
        ContentHandler.__init__(self)
        SGMLParser.__init__(self)
        self.config = config_

    def startElement(self, name, attrs):

        # we are only looking for data in 'outline' nodes.
        if name != 'outline':
            return

        # A type of 'rss' is meant to be used generically to indicate that
        # this is an entry in a subscription list, but some leave this
        # attribute off, and others have placed 'atom' in here
        if 'type' in attrs.keys():
            if attrs['type'] == 'link' and 'url' not in attrs.keys():
                # Auto-correct WordPress link manager OPML files
                attrs = dict(attrs.items())
                attrs['type'] = 'rss'
            if attrs['type'].lower() not in ['rss', 'atom']:
                return

        # The feed itself is supposed to be in an attribute named 'xmlUrl'
        # (note the camel casing), but this has proven to be problematic,
        # with the most common misspelling being in all lower-case
        if 'xmlUrl' not in attrs.keys() or not attrs['xmlUrl'].strip():
            for attribute in attrs.keys():
                if attribute.lower() == 'xmlurl' and attrs[attribute].strip():
                    attrs = dict(attrs.items())
                    attrs['xmlUrl'] = attrs[attribute]
                    break
            else:
                return

        # the text attribute is nominally required in OPML, but this
        # data is often found in a title attribute instead
        if 'text' not in attrs.keys() or not attrs['text'].strip():
            if 'title' not in attrs.keys() or not attrs['title'].strip():
                return
            attrs = dict(attrs.items())
            attrs['text'] = attrs['title']

        # if we get this far, we either have a valid subscription list entry,
        # or one with a correctable error.  Add it to the configuration, if
        # it is not already there.
        xml_url = attrs['xmlUrl']
        if not self.config.has_section(xml_url):
            self.config.add_section(xml_url)
            self.config.set(xml_url, 'name', self.unescape(attrs['text']))

    def unescape(self, text):
        parsed = self.entities.split(text)

        for i in range(1, len(parsed), 2):

            if parsed[i] in entitydefs.keys():
                # named entities
                codepoint = entitydefs[parsed[i]]
                match = self.entities.match(codepoint)
                if match:
                    parsed[i] = match.group(1)
                else:
                    parsed[i] = chr(ord(codepoint))

                # numeric entities
                if parsed[i].startswith('#'):
                    if parsed[i].startswith('#x'):
                        parsed[i] = chr(int(parsed[i][2:], 16))
                    else:
                        parsed[i] = chr(int(parsed[i][1:]))

        return u''.join(parsed).encode('utf-8')

    # SGML => SAX
    def unknown_starttag(self, name, attrs):
        attrs = dict(attrs)
        for attribute in attrs:
            try:
                attrs[attribute] = attrs[attribute].decode('utf-8')
            except Exception as e:
                print("WARNING: Broad exception caught. FIXME")
                print(e)
                print(traceback.print_exception(*sys.exc_info()))
                work = attrs[attribute].decode('iso-8859-1')
                work = u''.join([c in cp1252 and cp1252[c] or c for c in work])
                attrs[attribute] = work
        self.startElement(name, attrs)


# http://www.intertwingly.net/stories/2004/04/14/i18n.html#CleaningWindows
cp1252 = {
    chr(128): chr(8364),  # euro sign
    chr(130): chr(8218),  # single low-9 quotation mark
    chr(131): chr(402),  # latin small letter f with hook
    chr(132): chr(8222),  # double low-9 quotation mark
    chr(133): chr(8230),  # horizontal ellipsis
    chr(134): chr(8224),  # dagger
    chr(135): chr(8225),  # double dagger
    chr(136): chr(710),  # modifier letter circumflex accent
    chr(137): chr(8240),  # per mille sign
    chr(138): chr(352),  # latin capital letter s with caron
    chr(139): chr(8249),  # single left-pointing angle quotation mark
    chr(140): chr(338),  # latin capital ligature oe
    chr(142): chr(381),  # latin capital letter z with caron
    chr(145): chr(8216),  # left single quotation mark
    chr(146): chr(8217),  # right single quotation mark
    chr(147): chr(8220),  # left double quotation mark
    chr(148): chr(8221),  # right double quotation mark
    chr(149): chr(8226),  # bullet
    chr(150): chr(8211),  # en dash
    chr(151): chr(8212),  # em dash
    chr(152): chr(732),  # small tilde
    chr(153): chr(8482),  # trade mark sign
    chr(154): chr(353),  # latin small letter s with caron
    chr(155): chr(8250),  # single right-pointing angle quotation mark
    chr(156): chr(339),  # latin small ligature oe
    chr(158): chr(382),  # latin small letter z with caron
    chr(159): chr(376)}  # latin capital letter y with diaeresis

if __name__ == "__main__":
    # small main program which converts OPML into config.ini format

    config = ConfigParser()
    for opml in sys.argv[1:]:
        opml2config(urllib.urlopen(opml), config)
    config.write(sys.stdout)
