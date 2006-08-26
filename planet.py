#!/usr/bin/env python
"""The Planet aggregator.

A flexible and easy-to-use aggregator for generating websites.

Visit http://www.planetplanet.org/ for more information and to download
the latest version.

Requires Python 2.1, recommends 2.3.
"""

__authors__ = [ "Scott James Remnant <scott@netsplit.com>",
                "Jeff Waugh <jdub@perkypants.org>" ]
__license__ = "Python"


import os, sys

if __name__ == "__main__":
    config_file = "config.ini"
    offline = 0
    verbose = 0

    for arg in sys.argv[1:]:
        if arg == "-h" or arg == "--help":
            print "Usage: planet [options] [CONFIGFILE]"
            print
            print "Options:"
            print " -v, --verbose       DEBUG level logging during update"
            print " -o, --offline       Update the Planet from the cache only"
            print " -h, --help          Display this help message and exit"
            print
            sys.exit(0)
        elif arg == "-v" or arg == "--verbose":
            verbose = 1
        elif arg == "-o" or arg == "--offline":
            offline = 1
        elif arg.startswith("-"):
            print >>sys.stderr, "Unknown option:", arg
            sys.exit(1)
        else:
            config_file = arg

    if verbose:
        import planet
        planet.getLogger('DEBUG')

    if not offline:
        from planet import spider
        spider.spiderPlanet(config_file)

    from planet import splice
    doc = splice.splice(config_file)
    splice.apply(doc.toxml('utf-8'))
