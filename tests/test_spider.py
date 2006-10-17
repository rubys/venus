#!/usr/bin/env python

import unittest, os, glob, calendar, shutil
from planet.spider import filename, spiderFeed, spiderPlanet
from planet import feedparser, config
import planet

workdir = 'tests/work/spider/cache'
testfeed = 'tests/data/spider/testfeed%s.atom'
configfile = 'tests/data/spider/config.ini'

class SpiderTest(unittest.TestCase):
    def setUp(self):
        # silence errors
        planet.logger = None
        planet.getLogger('CRITICAL')

        try:
             os.makedirs(workdir)
        except:
             self.tearDown()
             os.makedirs(workdir)
    
    def tearDown(self):
        shutil.rmtree(workdir)
        os.removedirs(os.path.split(workdir)[0])

    def test_filename(self):
        self.assertEqual(os.path.join('.', 'example.com,index.html'),
            filename('.', 'http://example.com/index.html'))
        self.assertEqual(os.path.join('.',
            'planet.intertwingly.net,2006,testfeed1,1'),
            filename('.', u'tag:planet.intertwingly.net,2006:testfeed1,1'))
        self.assertEqual(os.path.join('.',
            '00000000-0000-0000-0000-000000000000'),
            filename('.', u'urn:uuid:00000000-0000-0000-0000-000000000000'))

        # Requires Python 2.3
        try:
            import encodings.idna
        except:
            return
        self.assertEqual(os.path.join('.', 'xn--8ws00zhy3a.com'),
            filename('.', u'http://www.\u8a79\u59c6\u65af.com/'))

    def test_spiderFeed(self):
        config.load(configfile)
        spiderFeed(testfeed % '1b')
        files = glob.glob(workdir+"/*")
        files.sort()

        # verify that exactly four files + one sources dir were produced
        self.assertEqual(5, len(files))

        # verify that the file names are as expected
        self.assertTrue(os.path.join(workdir,
            'planet.intertwingly.net,2006,testfeed1,1') in files)

        # verify that the file timestamps match atom:updated
        data = feedparser.parse(files[2])
        self.assertEqual(['application/atom+xml'], [link.type
            for link in data.entries[0].source.links if link.rel=='self'])
        self.assertEqual('one', data.entries[0].source.planet_name)
        self.assertEqual(os.stat(files[2]).st_mtime,
            calendar.timegm(data.entries[0].updated_parsed))

    def test_spiderUpdate(self):
        spiderFeed(testfeed % '1a')
        self.test_spiderFeed()

    def test_spiderPlanet(self):
        config.load(configfile)
        spiderPlanet()
        files = glob.glob(workdir+"/*")

        # verify that exactly eight files + 1 source dir were produced
        self.assertEqual(13, len(files))

        # verify that the file names are as expected
        self.assertTrue(os.path.join(workdir,
            'planet.intertwingly.net,2006,testfeed1,1') in files)
        self.assertTrue(os.path.join(workdir,
            'planet.intertwingly.net,2006,testfeed2,1') in files)

        data = feedparser.parse(workdir + 
            '/planet.intertwingly.net,2006,testfeed3,1')
        self.assertEqual(['application/rss+xml'], [link.type
            for link in data.entries[0].source.links if link.rel=='self'])
        self.assertEqual('three', data.entries[0].source.author_detail.name)

