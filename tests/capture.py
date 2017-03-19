#!/usr/bin/env python
# coding=utf-8

"""
While unit tests are intended to be independently executable, it often
is helpful to ensure that some downstream tasks can be run with the
exact output produced by upstream tasks.

This script captures such output.  It should be run whenever there is
a major change in the contract between stages
"""

import os
import shutil
import sys

# move up a directory
sys.path.insert(0, os.path.split(sys.path[0])[0])
os.chdir(sys.path[0])

# copy spider output to splice input
import planet
from planet import spider, config

planet.getLogger('CRITICAL', None)

config.load('tests/data/spider/config.ini')
spider.spiderPlanet()
if os.path.exists('tests/data/splice/cache'):
    shutil.rmtree('tests/data/splice/cache')
shutil.move('tests/work/spider/cache', 'tests/data/splice/cache')


with open('tests/data/spider/config.ini') as source, \
        open('tests/data/splice/config.ini', 'w') as dest1:
    dest1.write(source.read().replace('/work/spider/', '/data/splice/'))

with open('tests/data/spider/config.ini') as source, \
        open('tests/work/apply_config.ini', 'w') as dest2:
    dest2.write(source.read().replace('[Planet]', '''[Planet]
    output_theme = asf
    output_dir = tests/work/apply'''))

# copy splice output to apply input
from planet import splice

with open('tests/data/apply/feed.xml', 'w') as fp:
    config.load('tests/data/splice/config.ini')
    data = splice.splice().toxml('utf-8')
    fp.write(data)

# copy apply output to config/reading-list input
config.load('tests/work/apply_config.ini')
splice.apply(data)
shutil.move('tests/work/apply/opml.xml', 'tests/data/config')

shutil.rmtree('tests/work')

import runtests
