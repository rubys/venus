""" Splice together a planet from a cache of feed entries """
import glob, os, time, shutil
from xml.dom import minidom
import planet, config, feedparser, reconstitute, shell
from reconstitute import createTextElement, date
from spider import filename

def splice():
    """ Splice together a planet from a cache of entries """
    import planet
    log = planet.getLogger(config.log_level())

    log.info("Loading cached data")
    cache = config.cache_directory()
    dir=[(os.stat(file).st_mtime,file) for file in glob.glob(cache+"/*")
        if not os.path.isdir(file)]
    dir.sort()
    dir.reverse()

    items=max([config.items_per_page(templ)
        for templ in config.template_files() or ['Planet']])

    doc = minidom.parseString('<feed xmlns="http://www.w3.org/2005/Atom"/>')
    feed = doc.documentElement

    # insert feed information
    createTextElement(feed, 'title', config.name())
    date(feed, 'updated', time.gmtime())    
    gen = createTextElement(feed, 'generator', config.generator())
    gen.setAttribute('uri', config.generator_uri())

    author = doc.createElement('author')
    createTextElement(author, 'name', config.owner_name())
    createTextElement(author, 'email', config.owner_email())
    feed.appendChild(author)

    if config.feed():
        createTextElement(feed, 'id', config.feed())
        link = doc.createElement('link')
        link.setAttribute('rel', 'self')
        link.setAttribute('href', config.feed())
        if config.feedtype():
            link.setAttribute('type', "application/%s+xml" % config.feedtype())
        feed.appendChild(link)

    if config.link():
        link = doc.createElement('link')
        link.setAttribute('rel', 'alternate')
        link.setAttribute('href', config.link())
        feed.appendChild(link)

    # insert entry information
    for mtime,file in dir[:items]:
        try:
            entry=minidom.parse(file)
            feed.appendChild(entry.documentElement)
        except:
            log.error("Error parsing %s", file)

    # insert subscription information
    feed.setAttribute('xmlns:planet',planet.xmlns)
    sources = config.cache_sources_directory()
    for sub in config.subscriptions():
        data=feedparser.parse(filename(sources,sub))
        if not data.feed: continue
        xdoc=minidom.parseString('''<planet:source xmlns:planet="%s"
             xmlns="http://www.w3.org/2005/Atom"/>\n''' % planet.xmlns)
        reconstitute.source(xdoc.documentElement, data.feed, data.bozo)
        feed.appendChild(xdoc.documentElement)

    return doc

def apply(doc):
    output_dir = config.output_dir()
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    log = planet.getLogger(config.log_level())

    # Go-go-gadget-template
    for template_file in config.template_files():
        shell.run(template_file, doc)

    # Process bill of materials
    for copy_file in config.bill_of_materials():
        dest = os.path.join(output_dir, copy_file)
        for template_dir in config.template_directories():
            source = os.path.join(template_dir, copy_file)
            if os.path.exists(source): break
        else:
            log.error('Unable to locate %s', copy_file)
            continue

        mtime = os.stat(source).st_mtime
        if not os.path.exists(dest) or os.stat(dest).st_mtime < mtime:
            dest_dir = os.path.split(dest)[0]
            if not os.path.exists(dest_dir): os.makedirs(dest_dir)

            log.info("Copying %s to %s", source, dest)
            shutil.copyfile(source, dest)
            shutil.copystat(source, dest)
