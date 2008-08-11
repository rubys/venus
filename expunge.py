#!/usr/bin/env python
"""
Main program to run just the expunge portion of planet
"""

import os.path
import sys
from planet import expunge, config

if __name__ == '__main__':

    if len(sys.argv) == 2 and os.path.isfile(sys.argv[1]):
        config.load(sys.argv[1])
        expunge.expungeCache()
    else:
        print "Usage:"
        print "  python %s config.ini" % sys.argv[0]
