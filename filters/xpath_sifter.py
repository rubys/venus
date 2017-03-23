# coding=utf-8
from __future__ import print_function

import libxml2
import sys

# parse options
options = dict(zip(sys.argv[1::2], sys.argv[2::2]))

# parse entry
doc = libxml2.parseDoc(sys.stdin.read())
ctxt = doc.xpathNewContext()
ctxt.xpathRegisterNs('atom', 'http://www.w3.org/2005/Atom')
ctxt.xpathRegisterNs('xhtml', 'http://www.w3.org/1999/xhtml')

# process requirements
if '--require' in options.keys():
    for xpath in options['--require'].split('\n'):
        if xpath and not ctxt.xpathEval(xpath):
            sys.exit(1)

# process exclusions
if '--exclude' in options.keys():
    for xpath in options['--exclude'].split('\n'):
        if xpath and ctxt.xpathEval(xpath):
            sys.exit(1)

# if we get this far, the feed is to be included
print(doc)
