# coding=utf-8
# make href attributes absolute, using base argument passed in

from __future__ import print_function

import sys

try:
    base = sys.argv[sys.argv.index('--base') + 1]
except ValueError:
    sys.stderr.write('Missing required argument: base\n')
    sys.exit()

from xml.dom import minidom, Node
from urlparse import urljoin


def rebase(node, newbase):
    if node.hasAttribute('href'):
        href = node.getAttribute('href')
        if href != urljoin(base, href):
            node.setAttribute('href', urljoin(base, href))
    for child in node.childNodes:
        if child.nodeType == Node.ELEMENT_NODE:
            rebase(child, newbase)


doc = minidom.parse(sys.stdin)
rebase(doc.documentElement, base)
print(doc.toxml('utf-8'))
