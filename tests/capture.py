#!/usr/bin/env python

"""
While unit tests are intended to be independently executable, it often
is helpful to ensure that some downstream tasks can be run with the
exact output produced by upstream tasks.

This script captures such output.  It should be run whenever there is
a major change in the contract between stages
"""

import shutil, os, sys

# move up a directory
sys.path.insert(0, os.path.split(sys.path[0])[0])
os.chdir(sys.path[0])

# copy spider output to splice input
import planet
from planet import spider, config
planet.getLogger('CRITICAL',None)

config.load('tests/data/spider/config.ini')
spider.spiderPlanet()
if os.path.exists('tests/data/splice/cache'):
    shutil.rmtree('tests/data/splice/cache')
shutil.move('tests/work/spider/cache', 'tests/data/splice/cache')

source=open('tests/data/spider/config.ini')
dest1=open('tests/data/splice/config.ini', 'w')
dest1.write(source.read().replace('/work/spider/', '/data/splice/'))
dest1.close()

source.seek(0)
dest2=open('tests/work/apply_config.ini', 'w')
dest2.write(source.read().replace('[Planet]', '''[Planet]
output_theme = asf
output_dir = tests/work/apply'''))
dest2.close()
source.close()

# copy splice output to apply input
from planet import splice
file=open('tests/data/apply/feed.xml', 'w')
config.load('tests/data/splice/config.ini')
data=splice.splice().toxml('utf-8')
file.write(data)
file.close()

# copy apply output to config/reading-list input
config.load('tests/work/apply_config.ini')
splice.apply(data)
shutil.move('tests/work/apply/opml.xml', 'tests/data/config')

shutil.rmtree('tests/work')

import runtests
