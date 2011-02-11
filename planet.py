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
    config_file = []
    offline = 0
    verbose = 0
    only_if_new = 0
    expunge = 0
    debug_splice = 0
    no_publish = 0

    for arg in sys.argv[1:]:
        if arg == "-h" or arg == "--help":
            print "Usage: planet [options] [CONFIGFILE]"
            print
            print "Options:"
            print " -v, --verbose       DEBUG level logging during update"
            print " -o, --offline       Update the Planet from the cache only"
            print " -h, --help          Display this help message and exit"
            print " -n, --only-if-new   Only spider new feeds"
            print " -x, --expunge       Expunge old entries from cache"
            print " --no-publish        Do not publish feeds using PubSubHubbub"
            print
            sys.exit(0)
        elif arg == "-v" or arg == "--verbose":
            verbose = 1
        elif arg == "-o" or arg == "--offline":
            offline = 1
        elif arg == "-n" or arg == "--only-if-new":
            only_if_new = 1
        elif arg == "-x" or arg == "--expunge":
            expunge = 1
        elif arg == "-d" or arg == "--debug-splice":
            debug_splice = 1
        elif arg == "--no-publish":
            no_publish = 1
        elif arg.startswith("-"):
            print >>sys.stderr, "Unknown option:", arg
            sys.exit(1)
        else:
            config_file.append(arg)

    from planet import config
    config.load(config_file or 'config.ini')

    if verbose:
        import planet
        planet.getLogger('DEBUG',config.log_format())

    if not offline:
        from planet import spider
        try:
            spider.spiderPlanet(only_if_new=only_if_new)
        except Exception, e:
            print e

    from planet import splice
    doc = splice.splice()

    if debug_splice:
        from planet import logger
        logger.info('writing debug.atom')
        debug=open('debug.atom','w')
        try:
            from lxml import etree
            from StringIO import StringIO
            tree = etree.tostring(etree.parse(StringIO(doc.toxml())))
            debug.write(etree.tostring(tree, pretty_print=True))
        except:
            debug.write(doc.toprettyxml(indent='  ', encoding='utf-8'))
        debug.close

    splice.apply(doc.toxml('utf-8'))

    if config.pubsubhubbub_hub() and not no_publish:
        from planet import publish
        publish.publish(config)

    if expunge:
        from planet import expunge
        expunge.expungeCache
