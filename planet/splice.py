""" Splice together a planet from a cache of feed entries """
import glob, os
from xml.dom import minidom
import config
from reconstitute import createTextElement

def splice(configFile):
    """ Splice together a planet from a cache of entries """
    import planet
    config.load(configFile)
    log = planet.getLogger(config.log_level())

    cache = config.cache_directory()
    dir=[(os.stat(file).st_mtime,file) for file in glob.glob(cache+"/*")]
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
    feed.setAttribute('xmlns:planet','http://planet.intertwingly.net/')
    for sub in config.feeds():
        name = config.feed_options(sub).get('name','')
        xsub = doc.createElement('planet:subscription')
        xlink = doc.createElement('link')
        xlink.setAttribute('rel','self')
        xlink.setAttribute('href',sub.decode('utf-8'))
        xsub.appendChild(xlink)
        xname = doc.createElement('planet:name')
        xname.appendChild(doc.createTextNode(name.decode('utf-8')))
        xsub.appendChild(xname)
        feed.appendChild(xsub)

    return doc
