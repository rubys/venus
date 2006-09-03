#!/usr/bin/env python
"""
Main program to run just the splice portion of planet
"""

import os.path
import sys
from planet import splice, config

if __name__ == '__main__':

    if len(sys.argv) == 2 and os.path.isfile(sys.argv[1]):
        config.load(sys.argv[1])
        doc = splice.splice()
        splice.apply(doc.toxml('utf-8'))
    else:
        print "Usage:"
        print "  python %s config.ini" % sys.argv[0]
