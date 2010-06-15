""" Splice together a planet from a cache of feed entries """
import glob, os, time, shutil
from xml.dom import minidom
import planet, config, feedparser, reconstitute, shell
from reconstitute import createTextElement, date
from spider import filename
from planet import idindex

def splice():
    """ Splice together a planet from a cache of entries """
    import planet
    log = planet.logger

    log.info("Loading cached data")
    cache = config.cache_directory()
    dir=[(os.stat(file).st_mtime,file) for file in glob.glob(cache+"/*")
        if not os.path.isdir(file)]
    dir.sort()
    dir.reverse()

    max_items=max([config.items_per_page(templ)
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

    if config.pubsubhubbub_hub():
        hub = doc.createElement('link')
        hub.setAttribute('rel', 'hub')
        hub.setAttribute('href', config.pubsubhubbub_hub())
        feed.appendChild(hub)

    if config.link():
        link = doc.createElement('link')
        link.setAttribute('rel', 'alternate')
        link.setAttribute('href', config.link())
        feed.appendChild(link)

    # insert subscription information
    sub_ids = []
    feed.setAttribute('xmlns:planet',planet.xmlns)
    sources = config.cache_sources_directory()
    for sub in config.subscriptions():
        data=feedparser.parse(filename(sources,sub))
        if data.feed.has_key('id'): sub_ids.append(data.feed.id)
        if not data.feed: continue

        # warn on missing links
        if not data.feed.has_key('planet_message'):
            if not data.feed.has_key('links'): data.feed['links'] = []

            for link in data.feed.links:
              if link.rel == 'self': break
            else:
              log.debug('missing self link for ' + sub)

            for link in data.feed.links:
              if link.rel == 'alternate' and 'html' in link.type: break
            else:
              log.debug('missing html link for ' + sub)

        xdoc=minidom.parseString('''<planet:source xmlns:planet="%s"
             xmlns="http://www.w3.org/2005/Atom"/>\n''' % planet.xmlns)
        reconstitute.source(xdoc.documentElement, data.feed, None, None)
        feed.appendChild(xdoc.documentElement)

    index = idindex.open()

    # insert entry information
    items = 0
    count = {}
    atomNS='http://www.w3.org/2005/Atom'
    new_feed_items = config.new_feed_items()
    for mtime,file in dir:
        if index != None:
            base = os.path.basename(file)
            if index.has_key(base) and index[base] not in sub_ids: continue

        try:
            entry=minidom.parse(file)

            # verify that this entry is currently subscribed to and that the
            # number of entries contributed by this feed does not exceed
            # config.new_feed_items
            entry.normalize()
            sources = entry.getElementsByTagNameNS(atomNS, 'source')
            if sources:
                ids = sources[0].getElementsByTagName('id')
                if ids:
                    id = ids[0].childNodes[0].nodeValue
                    count[id] = count.get(id,0) + 1
                    if new_feed_items and count[id] > new_feed_items: continue

                    if id not in sub_ids:
                        ids = sources[0].getElementsByTagName('planet:id')
                        if not ids: continue
                        id = ids[0].childNodes[0].nodeValue
                        if id not in sub_ids:
                          log.warn('Skipping: ' + id)
                        if id not in sub_ids: continue

            # add entry to feed
            feed.appendChild(entry.documentElement)
            items = items + 1
            if items >= max_items: break
        except:
            log.error("Error parsing %s", file)

    if index: index.close()

    return doc

def apply(doc):
    output_dir = config.output_dir()
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    log = planet.logger

    planet_filters = config.filters('Planet')

    # Go-go-gadget-template
    for template_file in config.template_files():
        output_file = shell.run(template_file, doc)

        # run any template specific filters
        if config.filters(template_file) != planet_filters:
            output = open(output_file).read()
            for filter in config.filters(template_file):
                if filter in planet_filters: continue
                if filter.find('>')>0:
                    # tee'd output
                    filter,dest = filter.split('>',1)
                    tee = shell.run(filter.strip(), output, mode="filter")
                    if tee:
                        output_dir = planet.config.output_dir()
                        dest_file = os.path.join(output_dir, dest.strip())
                        dest_file = open(dest_file,'w')
                        dest_file.write(tee)
                        dest_file.close()
                else:
                    # pipe'd output
                    output = shell.run(filter, output, mode="filter")
                    if not output:
                        os.unlink(output_file)
                        break
            else:
                handle = open(output_file,'w')
                handle.write(output)
                handle.close()

    # Process bill of materials
    for copy_file in config.bill_of_materials():
        dest = os.path.join(output_dir, copy_file)
        for template_dir in config.template_directories():
            source = os.path.join(template_dir, copy_file)
            if os.path.exists(source): break
        else:
            log.error('Unable to locate %s', copy_file)
            log.info("Template search path:")
            for template_dir in config.template_directories():
                log.info("    %s", os.path.realpath(template_dir))
            continue

        mtime = os.stat(source).st_mtime
        if not os.path.exists(dest) or os.stat(dest).st_mtime < mtime:
            dest_dir = os.path.split(dest)[0]
            if not os.path.exists(dest_dir): os.makedirs(dest_dir)

            log.info("Copying %s to %s", source, dest)
            if os.path.exists(dest): os.chmod(dest, 0644)
            shutil.copyfile(source, dest)
            shutil.copystat(source, dest)
