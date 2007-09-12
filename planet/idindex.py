from glob import glob
import os, sys

if __name__ == '__main__':
    rootdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, rootdir)

from planet.spider import filename
from planet import config

def open():
    try:
        cache = config.cache_directory()
        index=os.path.join(cache,'index')
        if not os.path.exists(index): return None
        import dbhash
        return dbhash.open(filename(index, 'id'),'w')
    except Exception, e:
        if e.__class__.__name__ == 'DBError': e = e.args[-1]
        from planet import logger as log
        log.error(str(e))

def destroy():
    from planet import logger as log
    cache = config.cache_directory()
    index=os.path.join(cache,'index')
    if not os.path.exists(index): return None
    idindex = filename(index, 'id')
    if os.path.exists(idindex): os.unlink(idindex)
    os.removedirs(index)
    log.info(idindex + " deleted")

def create():
    from planet import logger as log
    cache = config.cache_directory()
    index=os.path.join(cache,'index')
    if not os.path.exists(index): os.makedirs(index)
    import dbhash
    index = dbhash.open(filename(index, 'id'),'c')

    try:
        import libxml2
    except:
        libxml2 = False
        from xml.dom import minidom

    for file in glob(cache+"/*"):
        if os.path.isdir(file):
            continue
        elif libxml2:
            try:
                doc = libxml2.parseFile(file)
                ctxt = doc.xpathNewContext()
                ctxt.xpathRegisterNs('atom','http://www.w3.org/2005/Atom')
                entry = ctxt.xpathEval('/atom:entry/atom:id')
                source = ctxt.xpathEval('/atom:entry/atom:source/atom:id')
                if entry and source:
                    index[filename('',entry[0].content)] = source[0].content
                doc.freeDoc()
            except:
                log.error(file)
        else:
            try:
                doc = minidom.parse(file)
                doc.normalize()
                ids = doc.getElementsByTagName('id')
                entry = [e for e in ids if e.parentNode.nodeName == 'entry']
                source = [e for e in ids if e.parentNode.nodeName == 'source']
                if entry and source:
                    index[filename('',entry[0].childNodes[0].nodeValue)] = \
                        source[0].childNodes[0].nodeValue
                doc.freeDoc()
            except:
                log.error(file)

    log.info(str(len(index.keys())) + " entries indexed")
    index.close()

    return open()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: %s [-c|-d]' % sys.argv[0]
        sys.exit(1)

    config.load(sys.argv[1])

    if len(sys.argv) > 2 and sys.argv[2] == '-c':
        create()
    elif len(sys.argv) > 2 and sys.argv[2] == '-d':
        destroy()
    else:
        from planet import logger as log
        index = open()
        if index:
            log.info(str(len(index.keys())) + " entries indexed")
            index.close()
        else:
            log.info("no entries indexed")
