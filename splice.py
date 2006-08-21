#!/usr/bin/env python
"""
Main program to run just the splice portion of planet
"""

import os.path
import sys
from planet import splice

if __name__ == '__main__':

    if len(sys.argv) == 2 and os.path.isfile(sys.argv[1]):
        # at the moment, we don't have template support, so we cheat and
        # simply insert a XSLT processing instruction
        doc = splice.splice(sys.argv[1])
        splice.apply(doc.toxml('utf-8'))
    else:
        print "Usage:"
        print "  python %s config.ini" % sys.argv[0]
