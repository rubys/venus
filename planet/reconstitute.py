# coding=utf-8
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
import re
import sys
import time
import traceback
from hashlib import md5
from xml.dom import Node, minidom
from xml.sax.saxutils import escape

from html5lib import html5parser, treebuilders

import config
import planet

try:
    unichr
    chr = unichr # Python2
except NameError:
    pass # Python3

illegal_xml_chars = re.compile("[\x01-\x08\x0B\x0C\x0E-\x1F]", re.UNICODE)


def createTextElement(parent, name, value):
    """ utility function to create a child element with the specified text"""
    if not value:
        return
    if isinstance(value, str):
        try:
            value = value.decode('utf-8')
        except Exception as e:
            print("WARNING: Broad exception caught. FIXME")
            print(e)
            print(traceback.print_exception(*sys.exc_info()))
            value = value.decode('iso-8859-1')
    value = illegal_xml_chars.sub(invalidate, value)
    xdoc = parent.ownerDocument
    xelement = xdoc.createElement(name)
    xelement.appendChild(xdoc.createTextNode(value))
    parent.appendChild(xelement)
    return xelement


def invalidate(c):
    """ replace invalid characters """
    return u'<abbr title="U+%s">\ufffd</abbr>' % \
           ('000' + hex(ord(c.group(0)))[2:])[-4:]


def ncr2c(value):
    """ convert numeric character references to characters """
    value = value.group(1)
    if value.startswith('x'):
        value = chr(int(value[1:], 16))
    else:
        value = chr(int(value))
    return value


nonalpha = re.compile('\W+', re.UNICODE)


def cssid(name):
    """ generate a css id from a name """
    try:
        name = nonalpha.sub('-', name.decode('utf-8')).lower().encode('utf-8')
    except Exception as e:
        print("WARNING: Broad exception caught. FIXME")
        print(e)
        print(traceback.print_exception(*sys.exc_info()))
        name = nonalpha.sub('-', name).lower()
    return name.strip('-')


def id(xentry, entry):
    """ copy or compute an id for the entry """

    if 'id' in entry.keys() and entry.id:
        entry_id = entry.id
        if hasattr(entry_id, 'values'):
            entry_id = entry_id.values()[0]
    elif 'link' in entry.keys() and entry.link:
        entry_id = entry.link
    elif 'title' in entry.keys() and entry.title:
        entry_id = (entry.title_detail.base + "/" + md5(entry.title).hexdigest())
    elif 'summary' in entry.keys() and entry.summary and 'summary_detail' in entry.keys() and entry.summary_detail:
        entry_id = (entry.summary_detail.base + "/" + md5(entry.summary).hexdigest())
    elif 'content' in entry.keys() and entry.content:

        entry_id = (entry.content[0].base + "/" + md5(entry.content[0].value).hexdigest())
    else:
        return

    if xentry:
        createTextElement(xentry, 'id', entry_id)
    return entry_id


def links(xentry, entry):
    """ copy links to the entry """
    if 'links' not in entry.keys():
        entry['links'] = []
        if 'link' in entry.keys():
            entry['links'].append({'rel': 'alternate', 'href': entry.link})
    xdoc = xentry.ownerDocument
    for link in entry['links']:
        if 'href' not in link.keys():
            continue
        xlink = xdoc.createElement('link')
        xlink.setAttribute('href', link.get('href'))
        if 'type' in link.keys():
            xlink.setAttribute('type', link.get('type'))
        if 'rel' in link.keys():
            xlink.setAttribute('rel', link.get('rel', None))
        if 'title' in link.keys():
            xlink.setAttribute('title', link.get('title'))
        if 'length' in link.keys():
            xlink.setAttribute('length', link.get('length'))
        xentry.appendChild(xlink)


def date(xentry, name, parsed):
    """ insert a date-formated element into the entry """
    if not parsed:
        return
    formatted = time.strftime("%Y-%m-%dT%H:%M:%SZ", parsed)
    xdate = createTextElement(xentry, name, formatted)
    formatted = time.strftime(config.date_format(), parsed)
    xdate.setAttribute('planet:format', formatted.decode('utf-8'))


def category(xentry, tag):
    xtag = xentry.ownerDocument.createElement('category')
    if 'term' not in tag.keys() or not tag.term:
        return
    xtag.setAttribute('term', tag.get('term'))
    if 'scheme' in tag.keys() and tag.scheme:
        xtag.setAttribute('scheme', tag.get('scheme'))
    if 'label' in tag.keys() and tag.label:
        xtag.setAttribute('label', tag.get('label'))
    xentry.appendChild(xtag)


def author(xentry, name, detail):
    """ insert an author-like element into the entry """
    if not detail:
        return
    xdoc = xentry.ownerDocument
    xauthor = xdoc.createElement(name)

    if detail.get('name', None):
        createTextElement(xauthor, 'name', detail.get('name'))
    else:
        xauthor.appendChild(xdoc.createElement('name'))

    createTextElement(xauthor, 'email', detail.get('email', None))
    createTextElement(xauthor, 'uri', detail.get('href', None))

    xentry.appendChild(xauthor)


def content(xentry, name, detail, bozo):
    """ insert a content-like element into the entry """
    if not detail or not detail.value:
        return

    data = None
    xdiv = '<div xmlns="http://www.w3.org/1999/xhtml">%s</div>'
    xdoc = xentry.ownerDocument
    xcontent = xdoc.createElement(name)

    if isinstance(detail.value, unicode):
        detail.value = detail.value.encode('utf-8')

    if 'type' not in detail.keys() or detail.type.lower().find('html') < 0:
        detail['value'] = escape(detail.value)
        detail['type'] = 'text/html'

    if detail.type.find('xhtml') >= 0 and not bozo:
        try:
            data = minidom.parseString(xdiv % detail.value).documentElement
            xcontent.setAttribute('type', 'xhtml')
        except Exception as e:
            print("WARNING: Broad exception caught. FIXME")
            print(e)
            print(traceback.print_exception(*sys.exc_info()))
            bozo = 1

    if detail.type.find('xhtml') < 0 or bozo:
        parser = html5parser.HTMLParser(tree=treebuilders.getTreeBuilder('dom'))
        html = parser.parse(xdiv % detail.value, encoding="utf-8")
        for body in html.documentElement.childNodes:
            if body.nodeType != Node.ELEMENT_NODE:
                continue
            if body.nodeName != 'body':
                continue
            for div in body.childNodes:
                if div.nodeType != Node.ELEMENT_NODE:
                    continue
                if div.nodeName != 'div':
                    continue
                try:
                    div.normalize()
                    if len(div.childNodes) == 1 and div.firstChild.nodeType == Node.TEXT_NODE:
                        data = div.firstChild
                        if illegal_xml_chars.search(data.data):
                            data = xdoc.createTextNode(
                                illegal_xml_chars.sub(invalidate, data.data))
                    else:
                        data = div
                        xcontent.setAttribute('type', 'xhtml')
                    break
                except Exception as e:
                    print("WARNING: Broad exception caught. FIXME")
                    print(e)
                    print(traceback.print_exception(*sys.exc_info()))
                    # in extremely nested cases, the Python runtime decides
                    # that normalize() must be in an infinite loop; mark
                    # the content as escaped html and proceed on...
                    xcontent.setAttribute('type', 'html')
                    data = xdoc.createTextNode(detail.value.decode('utf-8'))

    if data:
        xcontent.appendChild(data)

    if detail.get("language"):
        xcontent.setAttribute('xml:lang', detail.language)

    xentry.appendChild(xcontent)


def location(xentry, longitude, latitude):
    """ insert geo location into the entry """
    if not latitude or not longitude:
        return

    xlat = createTextElement(xentry, '%s:%s' % ('geo', 'lat'), '%f' % latitude)
    xlat.setAttribute('xmlns:%s' % 'geo', 'http://www.w3.org/2003/01/geo/wgs84_pos#')
    xlong = createTextElement(xentry, '%s:%s' % ('geo', 'long'), '%f' % longitude)
    xlong.setAttribute('xmlns:%s' % 'geo', 'http://www.w3.org/2003/01/geo/wgs84_pos#')

    xentry.appendChild(xlat)
    xentry.appendChild(xlong)


def source(xsource, source_, bozo, format_):
    """ copy source information to the entry """
    # xdoc = xsource.ownerDocument

    createTextElement(xsource, 'id', source_.get('id', source_.get('link', None)))
    createTextElement(xsource, 'icon', source_.get('icon', None))
    createTextElement(xsource, 'logo', source_.get('logo', None))

    if 'logo' not in source_.keys() and 'image' in source_.keys():
        createTextElement(xsource, 'logo', source_.image.get('href', None))

    for tag in source_.get('tags', []):
        category(xsource, tag)

    author(xsource, 'author', source_.get('author_detail', {}))
    for contributor in source_.get('contributors', []):
        author(xsource, 'contributor', contributor)

    if 'links' not in source_.keys() and 'href' in source_.keys():  # rss
        source_['links'] = [{'href': source_.get('href')}]
        if 'title' in source_.keys():
            source_['links'][0]['title'] = source_.get('title')
    links(xsource, source_)

    content(xsource, 'rights', source_.get('rights_detail', None), bozo)
    content(xsource, 'subtitle', source_.get('subtitle_detail', None), bozo)
    content(xsource, 'title', source_.get('title_detail', None), bozo)

    date(xsource, 'updated', source_.get('updated_parsed', time.gmtime()))

    if format_:
        source_['planet_format'] = format_
    if bozo is not None:
        source_['planet_bozo'] = bozo and 'true' or 'false'

    # propagate planet inserted information
    if 'planet_name' in source_.keys() and 'planet_css-id' not in source_.keys():
        source_['planet_css-id'] = cssid(source_['planet_name'])
    for key, value in source_.items():
        if key.startswith('planet_'):
            createTextElement(xsource, key.replace('_', ':', 1), value)


def reconstitute(feed, entry):
    """ create an entry document from a parsed feed """
    xdoc = minidom.parseString('<entry xmlns="http://www.w3.org/2005/Atom"/>\n')
    xentry = xdoc.documentElement
    xentry.setAttribute('xmlns:planet', planet.xmlns)

    if 'language' in entry.keys():
        xentry.setAttribute('xml:lang', entry.language)
    elif 'language' in feed.feed.keys():
        xentry.setAttribute('xml:lang', feed.feed.language)

    id(xentry, entry)
    links(xentry, entry)

    bozo = feed.bozo
    if 'title' not in entry.keys() or not entry.title:
        xentry.appendChild(xdoc.createElement('title'))

    content(xentry, 'title', entry.get('title_detail', None), bozo)
    content(xentry, 'summary', entry.get('summary_detail', None), bozo)
    content(xentry, 'content', entry.get('content', [None])[0], bozo)
    content(xentry, 'rights', entry.get('rights_detail', None), bozo)

    date(xentry, 'updated', entry_updated(feed.feed, entry, time.gmtime()))
    date(xentry, 'published', entry.get('published_parsed', None))

    if 'dc_date.taken' in entry.keys():
        date_taken = createTextElement(xentry, '%s:%s' % ('dc', 'date_Taken'), '%s' % entry.get('dc_date.taken', None))
        date_taken.setAttribute('xmlns:%s' % 'dc', 'http://purl.org/dc/elements/1.1/')
        xentry.appendChild(date_taken)

    for tag in entry.get('tags', []):
        category(xentry, tag)

    # known, simple text extensions
    for ns, name in [('feedburner', 'origLink')]:
        if '%s_%s' % (ns, name.lower()) in entry.keys() and ns in feed.namespaces.keys():
            xoriglink = createTextElement(xentry, '%s:%s' % (ns, name),
                                          entry['%s_%s' % (ns, name.lower())])
            xoriglink.setAttribute('xmlns:%s' % ns, feed.namespaces[ns])

    # geo location
    if 'where' in entry.keys() and \
                    'type' in entry.get('where', []).keys() and \
                    'coordinates' in entry.get('where', []).keys():
        where = entry.get('where', [])
        type_ = where.get('type', None)
        coordinates = where.get('coordinates', None)
        if type_ == 'Point':
            location(xentry, coordinates[0], coordinates[1])
        elif type_ == 'Box' or type_ == 'LineString' or type_ == 'Polygon':
            location(xentry, coordinates[0][0], coordinates[0][1])
    if 'geo_lat' in entry.keys() and 'geo_long' in entry.keys():
        location(xentry, float(entry.get('geo_long', None)), float(entry.get('geo_lat', None)))
    if 'georss_point' in entry.keys():
        coordinates = re.split('[,\s]', entry.get('georss_point'))
        location(xentry, float(coordinates[1]), float(coordinates[0]))
    elif 'georss_line' in entry.keys():
        coordinates = re.split('[,\s]', entry.get('georss_line'))
        location(xentry, float(coordinates[1]), float(coordinates[0]))
    elif 'georss_circle' in entry.keys():
        coordinates = re.split('[,\s]', entry.get('georss_circle'))
        location(xentry, float(coordinates[1]), float(coordinates[0]))
    elif 'georss_box' in entry.keys():
        coordinates = re.split('[,\s]', entry.get('georss_box'))
        location(xentry, (float(coordinates[1]) + float(coordinates[3])) / 2, (float(coordinates[0]) + float(coordinates[2])) / 2)
    elif 'georss_polygon' in entry.keys():
        coordinates = re.split('[,\s]', entry.get('georss_polygon'))
        location(xentry, float(coordinates[1]), float(coordinates[0]))

    # author / contributor
    author_detail = entry.get('author_detail', {})
    if author_detail and 'name' not in author_detail.keys() and \
                    'planet_name' in feed.feed.keys():
        author_detail['name'] = feed.feed['planet_name']
    author(xentry, 'author', author_detail)
    for contributor in entry.get('contributors', []):
        author(xentry, 'contributor', contributor)

    # merge in planet:* from feed (or simply use the feed if no source)
    src = entry.get('source')
    if src:
        for name, value in feed.feed.items():
            if name.startswith('planet_'):
                src[name] = value
        if 'id' in feed.feed.keys():
            src['planet_id'] = feed.feed.id
    else:
        src = feed.feed

    # source:author
    src_author = src.get('author_detail', {})
    if (not author_detail or 'name' not in author_detail.keys()) and \
                    'name' not in src_author.keys() and 'planet_name' in feed.feed.keys():
        if src_author:
            src_author = src_author.__class__(src_author.copy())
        src['author_detail'] = src_author
        src_author['name'] = feed.feed['planet_name']

    # source
    xsource = xdoc.createElement('source')
    source(xsource, src, bozo, feed.version)
    xentry.appendChild(xsource)

    return xdoc


def entry_updated(feed, entry, default=None):
    chks = ((entry, 'updated_parsed'),
            (entry, 'published_parsed'),
            (feed, 'updated_parsed'),
            (feed, 'published_parsed'),)
    for node, field in chks:
        if field in node.keys() and node[field]:
            return node[field]
    return default
