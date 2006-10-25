#!/usr/bin/env python
import os, sys, ConfigParser, shutil, glob
venus_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,venus_base)

if __name__ == "__main__":

    if sys.argv[1] == '-v' or sys.argv[1] == '--verbose':
        import planet
        planet.getLogger('DEBUG',None)
        del sys.argv[1]

    from planet import config
    config.parser = ConfigParser.ConfigParser()
    config.parser.add_section('Planet')
    config.parser.add_section(sys.argv[1])
    work = reduce(os.path.join, ['tests','work','reconsititute'], venus_base)
    output = os.path.join(work, 'output')
    config.parser.set('Planet','cache_directory',work)
    config.parser.set('Planet','output_dir',output)
    config.parser.set('Planet','template_files','themes/common/atom.xml.xslt')

    for name, value in zip(sys.argv[2::2],sys.argv[3::2]):
        config.parser.set(sys.argv[1], name.lstrip('-'), value)

    from planet import spider
    spider.spiderPlanet(only_if_new=False)

    from planet import feedparser
    for source in glob.glob(os.path.join(work, 'sources/*')):
        feed = feedparser.parse(source).feed
        if feed.has_key('title'):
            config.parser.set('Planet','name',feed.title_detail.value)
        if feed.has_key('link'):
            config.parser.set('Planet','link',feed.link)
        if feed.has_key('author_detail'):
            if feed.author_detail.has_key('name'):
                config.parser.set('Planet','owner_name',feed.author_detail.name)
            if feed.author_detail.has_key('email'):
                config.parser.set('Planet','owner_email',feed.author_detail.email)

    from planet import splice
    doc = splice.splice()
    splice.apply(doc.toxml('utf-8'))

    atom = open(os.path.join(output,'atom.xml')).read()

    shutil.rmtree(work)
    os.removedirs(os.path.dirname(work))

    print atom
