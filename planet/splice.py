""" Splice together a planet from a cache of feed entries """
import glob, os
from xml.dom import minidom
import planet, config, feedparser, reconstitute
from reconstitute import createTextElement
from spider import filename

def splice(configFile):
    """ Splice together a planet from a cache of entries """
    import planet
    config.load(configFile)
    log = planet.getLogger(config.log_level())

    cache = config.cache_directory()
    dir=[(os.stat(file).st_mtime,file) for file in glob.glob(cache+"/*")
        if not os.path.isdir(file)]
    dir.sort()
    dir.reverse()

    items=max([config.items_per_page(templ)
        for templ in config.template_files()])

    doc = minidom.parseString('<feed xmlns="http://www.w3.org/2005/Atom"/>')
    feed = doc.documentElement

    # insert Google/LiveJournal's noindex
    feed.setAttribute('indexing:index','no')
    feed.setAttribute('xmlns:indexing','urn:atom-extension:indexing')

    # insert feed information
    createTextElement(feed, 'title', config.name())

    # insert entry information
    for mtime,file in dir[:items]:
        entry=minidom.parse(file)
        feed.appendChild(entry.documentElement)

    # insert subscription information
    feed.setAttribute('xmlns:planet',planet.xmlns)
    sources = config.cache_sources_directory()
    for sub in config.feeds():
        data=feedparser.parse(filename(sources,sub))
        if not data.feed: continue
        xdoc=minidom.parseString('''<planet:source xmlns:planet="%s"
             xmlns="http://www.w3.org/2005/Atom"/>\n''' % planet.xmlns)
        reconstitute.source(xdoc.documentElement, data.feed, data.bozo)
        feed.appendChild(xdoc.documentElement)

    return doc
