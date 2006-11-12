"""
Reconstitute an entry document from the output of the Universal Feed Parser.

The main entry point is called 'reconstitute'.  Input parameters are:

  results: this is the entire hash table return by the UFP
  entry:   this is the entry in the hash that you want reconstituted

The value returned is an XML DOM.  Every effort is made to convert
everything to unicode, and text fields into either plain text or
well formed XHTML.

Todo:
  * extension elements
"""
import re, time, md5, sgmllib
from xml.sax.saxutils import escape
from xml.dom import minidom
from BeautifulSoup import BeautifulSoup
from xml.parsers.expat import ExpatError
import planet, config

illegal_xml_chars = re.compile("[\x01-\x08\x0B\x0C\x0E-\x1F]")

def createTextElement(parent, name, value):
    """ utility function to create a child element with the specified text"""
    if not value: return
    if isinstance(value,str):
        try:
            value=value.decode('utf-8')
        except:
            value=value.decode('iso-8859-1')
    xdoc = parent.ownerDocument
    xelement = xdoc.createElement(name)
    xelement.appendChild(xdoc.createTextNode(value))
    parent.appendChild(xelement)
    return xelement

def invalidate(c): 
    """ replace invalid characters """
    return '<acronym title="U+%s">\xef\xbf\xbd</acronym>' % \
        ('000' + hex(ord(c.group(0)))[2:])[-4:]

def ncr2c(value):
    """ convert numeric character references to characters """
    value=value.group(1)
    if value.startswith('x'):
        value=unichr(int(value[1:],16))
    else:
        value=unichr(int(value))
    return value

def normalize(text, bozo):
    """ convert everything to well formed XML """
    if text.has_key('type'):
        if text.type.lower().find('html')<0:
            text['value'] = escape(text.value)
            text['type'] = 'text/html'
        if text.type.lower() == 'text/html' or bozo:
            dom=BeautifulSoup(text.value,convertEntities="html")
            for tag in dom.findAll(True):
                for attr,value in tag.attrs:
                    value=sgmllib.charref.sub(ncr2c,value)
                    value=illegal_xml_chars.sub(u'\uFFFD',value)
                    tag[attr]=value
            text['value'] = illegal_xml_chars.sub(invalidate, str(dom))
    return text

def id(xentry, entry):
    """ copy or compute an id for the entry """

    if entry.has_key("id") and entry.id:
        entry_id = entry.id
    elif entry.has_key("link") and entry.link:
        entry_id = entry.link
    elif entry.has_key("title") and entry.title:
        entry_id = (entry.title_detail.base + "/" +
            md5.new(entry.title).hexdigest())
    elif entry.has_key("summary") and entry.summary:
        entry_id = (entry.summary_detail.base + "/" +
            md5.new(entry.summary).hexdigest())
    elif entry.has_key("content") and entry.content:

        entry_id = (entry.content[0].base + "/" + 
            md5.new(entry.content[0].value).hexdigest())
    else:
        return

    if xentry: createTextElement(xentry, 'id', entry_id)
    return entry_id

def links(xentry, entry):
    """ copy links to the entry """
    if not entry.has_key('links'):
       entry['links'] = []
       if entry.has_key('link'):
         entry['links'].append({'rel':'alternate', 'href':entry.link}) 
    xdoc = xentry.ownerDocument
    for link in entry.links:
        if not 'href' in link.keys(): continue
        xlink = xdoc.createElement('link')
        xlink.setAttribute('href', link.get('href'))
        if link.has_key('type'):
            xlink.setAttribute('type', link.get('type'))
        if link.has_key('rel'):
            xlink.setAttribute('rel', link.get('rel',None))
        if link.has_key('length'):
            xlink.setAttribute('length', link.get('length'))
        xentry.appendChild(xlink)

def date(xentry, name, parsed):
    """ insert a date-formated element into the entry """
    if not parsed: return
    formatted = time.strftime("%Y-%m-%dT%H:%M:%SZ", parsed)
    xdate = createTextElement(xentry, name, formatted)
    formatted = time.strftime(config.date_format(), parsed)
    xdate.setAttribute('planet:format', formatted)

def category(xentry, tag):
    xtag = xentry.ownerDocument.createElement('category')
    if tag.has_key('term') and tag.term:
        xtag.setAttribute('term', tag.get('term'))
    if tag.has_key('scheme') and tag.scheme:
        xtag.setAttribute('scheme', tag.get('scheme'))
    if tag.has_key('label') and tag.label:
        xtag.setAttribute('label', tag.get('label'))
    xentry.appendChild(xtag)

def author(xentry, name, detail):
    """ insert an author-like element into the entry """
    if not detail: return
    xdoc = xentry.ownerDocument
    xauthor = xdoc.createElement(name)

    createTextElement(xauthor, 'name', detail.get('name', None))
    createTextElement(xauthor, 'email', detail.get('email', None))
    createTextElement(xauthor, 'uri', detail.get('href', None))
        
    xentry.appendChild(xauthor)

def content(xentry, name, detail, bozo):
    """ insert a content-like element into the entry """
    if not detail or not detail.value: return
    normalize(detail, bozo)
    xdoc = xentry.ownerDocument
    xcontent = xdoc.createElement(name)

    try:
        # see if the resulting text is a well-formed XML fragment
        div = '<div xmlns="http://www.w3.org/1999/xhtml">%s</div>'
        if isinstance(detail.value,unicode):
            detail.value=detail.value.encode('utf-8')
        data = minidom.parseString(div % detail.value).documentElement

        if detail.value.find('<') < 0:
            xcontent.appendChild(data.firstChild)
        else:
            xcontent.setAttribute('type', 'xhtml')
            xcontent.appendChild(data)

    except ExpatError:
        # leave as html
        xcontent.setAttribute('type', 'html')
        xcontent.appendChild(xdoc.createTextNode(detail.value.decode('utf-8')))

    if detail.get("language"):
        xcontent.setAttribute('xml:lang', detail.language)

    xentry.appendChild(xcontent)

def source(xsource, source, bozo, format):
    """ copy source information to the entry """
    xdoc = xsource.ownerDocument

    createTextElement(xsource, 'id', source.get('id', source.get('link',None)))
    createTextElement(xsource, 'icon', source.get('icon', None))
    createTextElement(xsource, 'logo', source.get('logo', None))

    if not source.has_key('logo') and source.has_key('image'):
        createTextElement(xsource, 'logo', source.image.get('href',None))

    for tag in source.get('tags',[]):
        category(xsource, tag)

    author(xsource, 'author', source.get('author_detail',{}))
    for contributor in source.get('contributors',[]):
        author(xsource, 'contributor', contributor)

    links(xsource, source)

    content(xsource, 'rights', source.get('rights_detail',None), bozo)
    content(xsource, 'subtitle', source.get('subtitle_detail',None), bozo)
    content(xsource, 'title', source.get('title_detail',None), bozo)

    date(xsource, 'updated', source.get('updated_parsed',time.gmtime()))

    if format: source['planet_format'] = format
    if not bozo == None: source['planet_bozo'] = bozo and 'true' or 'false'

    # propagate planet inserted information
    for key, value in source.items():
        if key.startswith('planet_'):
            createTextElement(xsource, key.replace('_',':',1), value)

def reconstitute(feed, entry):
    """ create an entry document from a parsed feed """
    xdoc=minidom.parseString('<entry xmlns="http://www.w3.org/2005/Atom"/>\n')
    xentry=xdoc.documentElement
    xentry.setAttribute('xmlns:planet',planet.xmlns)

    if entry.has_key('language'):
        xentry.setAttribute('xml:lang', entry.language)
    elif feed.feed.has_key('language'):
        xentry.setAttribute('xml:lang', feed.feed.language)

    id(xentry, entry)
    links(xentry, entry)

    bozo = feed.bozo
    if not entry.has_key('title'):
        xentry.appendChild(xdoc.createElement('title'))

    content(xentry, 'title', entry.get('title_detail',None), bozo)
    content(xentry, 'summary', entry.get('summary_detail',None), bozo)
    content(xentry, 'content', entry.get('content',[None])[0], bozo)
    content(xentry, 'rights', entry.get('rights_detail',None), bozo)

    date(xentry, 'updated', entry_updated(feed.feed, entry, time.gmtime()))
    date(xentry, 'published', entry.get('published_parsed',None))

    for tag in entry.get('tags',[]):
        category(xentry, tag)

    # known, simple text extensions
    for ns,name in [('feedburner','origlink')]:
        if entry.has_key('%s_%s' % (ns,name)) and \
            feed.namespaces.has_key(ns):
            xoriglink = createTextElement(xentry, '%s:%s' % (ns,name),
                entry['%s_%s' % (ns,name)])
            xoriglink.setAttribute('xmlns:%s' % ns, feed.namespaces[ns])

    author_detail = entry.get('author_detail',{})
    if author_detail and not author_detail.has_key('name') and \
        feed.feed.has_key('planet_name'):
        author_detail['name'] = feed.feed['planet_name']
    author(xentry, 'author', author_detail)
    for contributor in entry.get('contributors',[]):
        author(xentry, 'contributor', contributor)

    xsource = xdoc.createElement('source')
    src = entry.get('source') or feed.feed
    src_author = src.get('author_detail',{})
    if (not author_detail or not author_detail.has_key('name')) and \
       not src_author.has_key('name') and  feed.feed.has_key('planet_name'):
       if src_author: src_author = src_author.__class__(src_author.copy())
       src['author_detail'] = src_author
       src_author['name'] = feed.feed['planet_name']
    source(xsource, src, bozo, feed.version)
    xentry.appendChild(xsource)

    return xdoc

def entry_updated(feed, entry, default = None):
    chks = ((entry, 'updated_parsed'),
            (entry, 'published_parsed'),
            (feed,  'updated_parsed'),)
    for node, field in chks:
        if node.has_key(field) and node[field]:
            return node[field]
    return default
