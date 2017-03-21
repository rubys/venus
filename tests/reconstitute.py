#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function

import ConfigParser
import glob
import os
import shutil
import sys

venus_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, venus_base)

if __name__ == "__main__":
    import planet

    planet.getLogger('WARN', None)

    hide_planet_ns = True

    while len(sys.argv) > 1:
        if sys.argv[1] == '-v' or sys.argv[1] == '--verbose':
            del sys.argv[1]
        elif sys.argv[1] == '-p' or sys.argv[1] == '--planet':
            hide_planet_ns = False
            del sys.argv[1]
        else:
            break

    parser = ConfigParser.ConfigParser()
    parser.add_section('Planet')
    parser.add_section(sys.argv[1])
    work = reduce(os.path.join, ['tests', 'work', 'reconsititute'], venus_base)
    output = os.path.join(work, 'output')
    filters = os.path.join(venus_base, 'filters')
    parser.set('Planet', 'cache_directory', work)
    parser.set('Planet', 'output_dir', output)
    parser.set('Planet', 'filter_directories', filters)
    if hide_planet_ns:
        parser.set('Planet', 'template_files', 'themes/common/atom.xml.xslt')
    else:
        parser.set('Planet', 'template_files', 'tests/data/reconstitute.xslt')

    for name, value in zip(sys.argv[2::2], sys.argv[3::2]):
        parser.set(sys.argv[1], name.lstrip('-'), value)

    from planet import config

    config.parser = parser

    from planet import spider

    spider.spiderPlanet(only_if_new=False)

    import feedparser

    for source in glob.glob(os.path.join(work, 'sources/*')):
        feed = feedparser.parse(source).feed
        if 'title' in feed.keys():
            config.parser.set('Planet', 'name', feed.title_detail.value)
        if 'link' in feed.keys():
            config.parser.set('Planet', 'link', feed.link)
        if 'author_detail' in feed.keys():
            if 'name' in feed.author_detail.keys():
                config.parser.set('Planet', 'owner_name', feed.author_detail.name)
            if 'email' in feed.author_detail.keys():
                config.parser.set('Planet', 'owner_email', feed.author_detail.email)

    from planet import splice

    doc = splice.splice()

    sources = doc.getElementsByTagName('planet:source')
    if hide_planet_ns and len(sources) == 1:
        source = sources[0]
        feed = source.parentNode
        child = feed.firstChild
        while child:
            next_ = child.nextSibling
            if child.nodeName not in ['planet:source', 'entry']:
                feed.removeChild(child)
            child = next_
        while source.hasChildNodes():
            child = source.firstChild
            source.removeChild(child)
            feed.insertBefore(child, source)
        atomNS = 'http://www.w3.org/2005/Atom'
        for source in doc.getElementsByTagNameNS(atomNS, 'source'):
            source.parentNode.removeChild(source)

    splice.apply(doc.toxml('utf-8'))

    if hide_planet_ns:
        atom_path = os.path.join(output, 'atom.xml')
    else:
        atom_path = os.path.join(output, 'reconstitute')

    with open(atom_path) as fp:
        atom = fp.read()

    shutil.rmtree(work)
    os.removedirs(os.path.dirname(work))

    print(atom)
