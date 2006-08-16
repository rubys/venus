#!/usr/bin/env python

import unittest, os, glob, calendar
from planet.spider import filename, spiderFeed, spiderPlanet
from planet import feedparser, config

workdir = 'tests/work/spider/cache'
testfeed = 'tests/data/spider/testfeed%s.atom'
configfile = 'tests/data/spider/config.ini'

class SpiderTest(unittest.TestCase):
    def setUp(self):
        try:
             os.makedirs(workdir)
        except:
             self.tearDown()
             os.makedirs(workdir)
    
    def tearDown(self):
        for file in glob.glob(workdir+"/*"):
             os.unlink(file)
        os.removedirs(workdir)

    def test_filename(self):
        self.assertEqual('./example.com,index.html',
            filename('.', 'http://example.com/index.html'))
        self.assertEqual('./www.xn--8ws00zhy3a.com',
            filename('.', u'http://www.\u8a79\u59c6\u65af.com/'))

    def test_spiderFeed(self):
        config.load(configfile)
        spiderFeed(testfeed % '1b')
        files = glob.glob(workdir+"/*")

        # verify that exactly four files were produced
        self.assertEqual(4, len(files))

        # verify that the file names are as expected
        self.assertTrue(workdir + 
            '/tag:planet.intertwingly.net,2006:testfeed1,1' in files)

        # verify that the file timestamps match atom:updated
        for file in files:
            data = feedparser.parse(file)
            self.assertTrue(data.entries[0].source.planet_name)
            self.assertEqual(os.stat(file).st_mtime,
                calendar.timegm(data.entries[0].updated_parsed))

    def test_spiderUpdate(self):
        spiderFeed(testfeed % '1a')
        self.test_spiderFeed()

    def test_spiderPlanet(self):
        spiderPlanet(configfile)
        files = glob.glob(workdir+"/*")

        # verify that exactly eight files were produced
        self.assertEqual(12, len(files))

        # verify that the file names are as expected
        self.assertTrue(workdir + 
            '/tag:planet.intertwingly.net,2006:testfeed1,1' in files)
        self.assertTrue(workdir + 
            '/tag:planet.intertwingly.net,2006:testfeed2,1' in files)

