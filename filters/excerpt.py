"""
Generate an excerpt from either the summary or a content of an entry.

Parameters:
  width:  maximum number of characters in the excerpt.  Default: 500
  omit:   whitespace delimited list of html tags to remove.  Default: none
  target: name of element created.  Default: planet:excerpt

Notes:
 * if 'img' is in the list of tags to be omitted <img> tags are replaced with
   hypertext links associated with the value of the 'alt' attribute.  If there
   is no alt attribute value, <img> is used instead.  If the parent element
   of the img tag is already an <a> tag, no additional hypertext links are
   added.
"""

import sys, xml.dom.minidom, textwrap
from xml.dom import Node, minidom

atomNS = 'http://www.w3.org/2005/Atom'
planetNS = 'http://planet.intertwingly.net/'

args = dict(zip([name.lstrip('-') for name in sys.argv[1::2]], sys.argv[2::2]))

wrapper = textwrap.TextWrapper(width=int(args.get('width','500')))
omit = args.get('omit', '').split()
target = args.get('target', 'planet:excerpt')

class copy:
    """ recursively copy a source to a target, up to a given width """

    def __init__(self, dom, source, target):
        self.dom = dom
        self.full = False
        self.text = []
        self.textlen = 0
        self.copyChildren(source, target)

    def copyChildren(self, source, target):
        """ copy child nodes of a source to the target """
        for child in source.childNodes:
            if child.nodeType == Node.ELEMENT_NODE:
                 self.copyElement(child, target)
            elif child.nodeType == Node.TEXT_NODE:
                 self.copyText(child.data, target)
            if self.full: break

    def copyElement(self, source, target):
        """ copy source element to the target """

        # check the omit list
        if source.nodeName in omit:
            if source.nodeName == 'img':
               return self.elideImage(source, target)
            return self.copyChildren(source, target)

        # copy element, attributes, and children
        child = self.dom.createElementNS(source.namespaceURI, source.nodeName)
        target.appendChild(child)
        for i in range(0, source.attributes.length):
            attr = source.attributes.item(i)
            child.setAttributeNS(attr.namespaceURI, attr.name, attr.value)
        self.copyChildren(source, child)

    def elideImage(self, source, target):
        """ copy an elided form of the image element to the target """
        alt = source.getAttribute('alt') or '<img>'
        src = source.getAttribute('src')

        if target.nodeName == 'a' or not src:
            self.copyText(alt, target)
        else:
            child = self.dom.createElement('a')
            child.setAttribute('href', src)
            self.copyText(alt, child)
            target.appendChild(child)

    def copyText(self, source, target):
        """ copy text to the target, until the point where it would wrap """
        if not source.isspace() and source.strip():
            self.text.append(source.strip())
        lines = wrapper.wrap(' '.join(self.text))
        if len(lines) == 1:
            target.appendChild(self.dom.createTextNode(source))
            self.textlen = len(lines[0])
        elif lines:
            excerpt = source[:len(lines[0])-self.textlen] + u' \u2026'
            target.appendChild(dom.createTextNode(excerpt))
            self.full = True

# select summary or content element
dom = minidom.parse(sys.stdin)
source = dom.getElementsByTagNameNS(atomNS, 'summary')
if not source:
    source = dom.getElementsByTagNameNS(atomNS, 'content')

# if present, recursively copy it to a planet:excerpt element
if source:
    if target.startswith('planet:'):
        dom.documentElement.setAttribute('xmlns:planet', planetNS)
    if target.startswith('atom:'): target = target.split(':',1)[1]
    excerpt = dom.createElementNS(planetNS, target)
    source[0].parentNode.appendChild(excerpt)
    copy(dom, source[0], excerpt)
    if source[0].nodeName == excerpt.nodeName:
        source[0].parentNode.removeChild(source[0])

# print out results
print dom.toxml('utf-8')
