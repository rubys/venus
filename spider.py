#!/usr/bin/env python
"""
Main program to run just the spider portion of planet
"""

import sys
from planet import spider, config

if __name__ == '__main__':

    config.load(sys.argv[1])

    if len(sys.argv) == 2:
        # spider all feeds 
        spider.spiderPlanet()
    elif len(sys.argv) > 2:
        # spider selected feeds 
        for feed in sys.argv[2:]:
            spider.spiderFeed(feed)
    else:
        print "Usage:"
        print "  python %s config.ini [URI URI ...]" % sys.argv[0]
