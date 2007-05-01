"""
Remap all images to take advantage of the Coral Content Distribution
Network <http://www.coralcdn.org/>.
"""

import re, sys, urlparse, xml.dom.minidom

entry = xml.dom.minidom.parse(sys.stdin).documentElement

for node in entry.getElementsByTagName('img'):
    if node.hasAttribute('src'):
        component = list(urlparse.urlparse(node.getAttribute('src')))
        if component[0] == 'http':
            component[1] = re.sub(r':(\d+)$', r'.\1', component[1])
            component[1] += '.nyud.net:8080'
            node.setAttribute('src', urlparse.urlunparse(component))

print entry.toxml('utf-8')
