from xml.sax import ContentHandler, make_parser, SAXParseException
from xml.sax.xmlreader import InputSource
from sgmllib import SGMLParser
from cStringIO import StringIO
from ConfigParser import ConfigParser
from htmlentitydefs import entitydefs
import re

# input = opml, output = ConfigParser
def opml2config(opml, config=None):

    if hasattr(opml, 'read'):
        opml = opml.read()

    if not config:
        config = ConfigParser()

    opmlParser = OpmlParser(config)

    try:
        # try SAX
        source = InputSource()
        source.setByteStream(StringIO(opml))
        parser = make_parser()
        parser.setContentHandler(opmlParser)
        parser.parse(source)
    except SAXParseException:
        # try as SGML
        opmlParser.feed(opml)

    return config

# Parse OPML via either SAX or SGML
class OpmlParser(ContentHandler,SGMLParser):
    entities = re.compile('&(#?\w+);')

    def __init__(self, config):
        ContentHandler.__init__(self)
        SGMLParser.__init__(self)
        self.config = config

    def startElement(self, name, attrs):

        # we are only looking for data in 'outline' nodes.
        if name != 'outline': return

        # A type of 'rss' is meant to be used generically to indicate that
        # this is an entry in a subscription list, but some leave this
        # attribute off, and others have placed 'atom' in here
        if attrs.has_key('type'):
            if attrs['type'] == 'link' and not attrs.has_key('url'):
                # Auto-correct WordPress link manager OPML files
                attrs = dict(attrs.items())
                attrs['type'] = 'rss'
            if attrs['type'].lower() not in['rss','atom']: return

        # The feed itself is supposed to be in an attribute named 'xmlUrl'
        # (note the camel casing), but this has proven to be problematic,
        # with the most common misspelling being in all lower-case
        if not attrs.has_key('xmlUrl') or not attrs['xmlUrl'].strip():
            for attribute in attrs.keys():
                if attribute.lower() == 'xmlurl' and attrs[attribute].strip():
                    attrs = dict(attrs.items())
                    attrs['xmlUrl'] = attrs[attribute]
                    break
            else:
                return

        # the text attribute is nominally required in OPML, but this
        # data is often found in a title attribute instead
        if not attrs.has_key('text') or not attrs['text'].strip():
            if not attrs.has_key('title') or not attrs['title'].strip(): return
            attrs = dict(attrs.items())
            attrs['text'] = attrs['title']

        # if we get this far, we either have a valid subscription list entry,
        # or one with a correctable error.  Add it to the configuration, if
        # it is not already there.
        xmlUrl = attrs['xmlUrl']
        if not self.config.has_section(xmlUrl):
            self.config.add_section(xmlUrl)
            self.config.set(xmlUrl, 'name', self.unescape(attrs['text']))

    def unescape(self, text):
        parsed = self.entities.split(text)

        for i in range(1,len(parsed),2):

            if parsed[i] in entitydefs.keys():
                # named entities
                codepoint=entitydefs[parsed[i]]
                match=self.entities.match(codepoint)
                if match:
                    parsed[i]=match.group(1)
                else:
                    parsed[i]=unichr(ord(codepoint))

                # numeric entities
                if parsed[i].startswith('#'):
                    if parsed[i].startswith('#x'):
                        parsed[i]=unichr(int(parsed[i][2:],16))
                    else:
                        parsed[i]=unichr(int(parsed[i][1:]))

        return u''.join(parsed).encode('utf-8')
    # SGML => SAX
    def unknown_starttag(self, name, attrs):
        attrs = dict(attrs)
        for attribute in attrs:
            try:
                attrs[attribute] = attrs[attribute].decode('utf-8')
            except:
                work = attrs[attribute].decode('iso-8859-1')
                work = u''.join([c in cp1252 and cp1252[c] or c for c in work])
                attrs[attribute] = work
        self.startElement(name, attrs)

# http://www.intertwingly.net/stories/2004/04/14/i18n.html#CleaningWindows
cp1252 = {
  unichr(128): unichr(8364), # euro sign
  unichr(130): unichr(8218), # single low-9 quotation mark
  unichr(131): unichr( 402), # latin small letter f with hook
  unichr(132): unichr(8222), # double low-9 quotation mark
  unichr(133): unichr(8230), # horizontal ellipsis
  unichr(134): unichr(8224), # dagger
  unichr(135): unichr(8225), # double dagger
  unichr(136): unichr( 710), # modifier letter circumflex accent
  unichr(137): unichr(8240), # per mille sign
  unichr(138): unichr( 352), # latin capital letter s with caron
  unichr(139): unichr(8249), # single left-pointing angle quotation mark
  unichr(140): unichr( 338), # latin capital ligature oe
  unichr(142): unichr( 381), # latin capital letter z with caron
  unichr(145): unichr(8216), # left single quotation mark
  unichr(146): unichr(8217), # right single quotation mark
  unichr(147): unichr(8220), # left double quotation mark
  unichr(148): unichr(8221), # right double quotation mark
  unichr(149): unichr(8226), # bullet
  unichr(150): unichr(8211), # en dash
  unichr(151): unichr(8212), # em dash
  unichr(152): unichr( 732), # small tilde
  unichr(153): unichr(8482), # trade mark sign
  unichr(154): unichr( 353), # latin small letter s with caron
  unichr(155): unichr(8250), # single right-pointing angle quotation mark
  unichr(156): unichr( 339), # latin small ligature oe
  unichr(158): unichr( 382), # latin small letter z with caron
  unichr(159): unichr( 376)} # latin capital letter y with diaeresis

if __name__ == "__main__":
    # small main program which converts OPML into config.ini format
    import sys, urllib
    config = ConfigParser()
    for opml in sys.argv[1:]:
        opml2config(urllib.urlopen(opml), config)
    config.write(sys.stdout)
