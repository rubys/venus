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
    if isinstance(value,str): value=value.decode('utf-8')
    xdoc = parent.ownerDocument
    xelement = xdoc.createElement(name)
    xelement.appendChild(xdoc.createTextNode(value))
    parent.appendChild(xelement)
    return xelement

def invalidate(c): 
    """ replace invalid characters """
    return '<acronym title="U+%s">\xef\xbf\xbd</acronym>' % \
        hex(ord(c.group(0)))[2:].rjust(4,'0')

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
    if not entry.has_key('links'): return
    xdoc = xentry.ownerDocument
    for link in entry.links:
        if not 'href' in link.keys(): continue
        xlink = xdoc.createElement('link')
        xlink.setAttribute('type', link.get('type',None))
        xlink.setAttribute('href', link.href)
        xlink.setAttribute('rel', link.get('rel',None))
        xentry.appendChild(xlink)

def date(xentry, name, parsed):
    """ insert a date-formated element into the entry """
    if not parsed: return
    formatted = time.strftime("%Y-%m-%dT%H:%M:%SZ", parsed)
    xdate = createTextElement(xentry, name, formatted)
    formatted = time.strftime(config.date_format(), parsed)
    xdate.setAttribute('planet:format', formatted)

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

    if detail.language:
        xcontent.setAttribute('xml:lang', detail.language)

    xentry.appendChild(xcontent)

def source(xsource, source, bozo):
    """ copy source information to the entry """
    xdoc = xsource.ownerDocument

    createTextElement(xsource, 'id', source.get('id', None))
    createTextElement(xsource, 'icon', source.get('icon', None))
    createTextElement(xsource, 'logo', source.get('logo', None))

    author(xsource, 'author', source.get('author_detail',None))
    for contributor in source.get('contributors',[]):
        author(xsource, 'contributor', contributor)

    links(xsource, source)

    content(xsource, 'rights', source.get('rights_detail',None), bozo)
    content(xsource, 'subtitle', source.get('subtitle_detail',None), bozo)
    content(xsource, 'title', source.get('title_detail',None), bozo)

    date(xsource, 'updated', source.get('updated_parsed',None))

    # propagate planet inserted information
    for key, value in source.items():
        if key.startswith('planet_'):
            createTextElement(xsource, key.replace('_',':',1), value)

def reconstitute(feed, entry):
    """ create an entry document from a parsed feed """
    xdoc=minidom.parseString('<entry xmlns="http://www.w3.org/2005/Atom"/>\n')
    xentry=xdoc.documentElement
    xentry.setAttribute('xmlns:planet',planet.xmlns)

    id(xentry, entry)
    links(xentry, entry)

    bozo = feed.bozo
    content(xentry, 'title', entry.get('title_detail',None), bozo)
    content(xentry, 'summary', entry.get('summary_detail',None), bozo)
    content(xentry, 'content', entry.get('content',[None])[0], bozo)
    content(xentry, 'rights', entry.get('rights_detail',None), bozo)

    date(xentry, 'updated', entry.get('updated_parsed',time.gmtime()))
    date(xentry, 'published', entry.get('published_parsed',None))

    author(xentry, 'author', entry.get('author_detail',None))
    for contributor in entry.get('contributors',[]):
        author(xentry, 'contributor', contributor)

    xsource = xdoc.createElement('source')
    source(xsource, entry.get('source', feed.feed), bozo)
    xentry.appendChild(xsource)

    return xdoc
