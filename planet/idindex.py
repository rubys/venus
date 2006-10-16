from glob import glob
import os, sys, dbhash

if __name__ == '__main__':
    rootdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, rootdir)

from planet.spider import filename
from planet import config

def open():
    cache = config.cache_directory()
    index=os.path.join(cache,'index')
    if not os.path.exists(index): return None
    return dbhash.open(filename(index, 'id'),'w')

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
    import libxml2
    from planet import logger as log
    cache = config.cache_directory()
    index=os.path.join(cache,'index')
    if not os.path.exists(index): os.makedirs(index)
    index = dbhash.open(filename(index, 'id'),'c')

    for file in glob(cache+"/*"):
        if not os.path.isdir(file):
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
