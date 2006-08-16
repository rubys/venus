"""
Main program to run just the spider portion of planet
"""

import sys
from planet import spider, config

if __name__ == '__main__':

    if len(sys.argv) == 2:
        # spider all feeds 
        spider.spiderPlanet(sys.argv[1])
    elif len(sys.argv) > 2 and os.path.isdir(sys.argv[1]):
        # spider selected feeds 
        config.load(sys.argv[1])
        for feed in sys.argv[2:]:
            spider.spiderFeed(feed)
    else:
        print "Usage:"
        print "  python %s config.ini [URI URI ...]" % sys.argv[0]
