#!/usr/bin/env python

import unittest, os, glob, calendar, shutil, time
from planet.spider import filename, spiderPlanet, writeCache
from planet import feedparser, config
import planet

workdir = 'tests/work/spider/cache'
testfeed = 'tests/data/spider/testfeed%s.atom'
configfile = 'tests/data/spider/config.ini'

class SpiderTest(unittest.TestCase):
    def setUp(self):
        # silence errors
        self.original_logger = planet.logger
        planet.getLogger('CRITICAL',None)

        try:
             os.makedirs(workdir)
        except:
             self.tearDown()
             os.makedirs(workdir)
    
    def tearDown(self):
        shutil.rmtree(workdir)
        os.removedirs(os.path.split(workdir)[0])
        planet.logger = self.original_logger

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

    def spiderFeed(self, feed_uri):
        feed_info = feedparser.parse('<feed/>')
        data = feedparser.parse(feed_uri)
        writeCache(feed_uri, feed_info, data)

    def verify_spiderFeed(self):
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
        self.assertEqual('2006-01-03T00:00:00Z', data.entries[0].updated)
        self.assertEqual(os.stat(files[2]).st_mtime,
            calendar.timegm(data.entries[0].updated_parsed))

    def test_spiderFeed(self):
        config.load(configfile)
        self.spiderFeed(testfeed % '1b')
        self.verify_spiderFeed()

    def test_spiderFeed_retroactive_filter(self):
        config.load(configfile)
        self.spiderFeed(testfeed % '1b')
        self.assertEqual(5, len(glob.glob(workdir+"/*")))
        config.parser.set('Planet', 'filter', 'two')
        self.spiderFeed(testfeed % '1b')
        self.assertEqual(1, len(glob.glob(workdir+"/*")))

    def test_spiderUpdate(self):
        config.load(configfile)
        self.spiderFeed(testfeed % '1a')
        self.spiderFeed(testfeed % '1b')
        self.verify_spiderFeed()

    def test_spiderFeedUpdatedEntries(self):
        config.load(configfile)
        self.spiderFeed(testfeed % '4')
        self.assertEqual(2, len(glob.glob(workdir+"/*")))
        data = feedparser.parse(workdir + 
            '/planet.intertwingly.net,2006,testfeed4')
        self.assertEqual(u'three', data.entries[0].content[0].value)

    def verify_spiderPlanet(self):
        files = glob.glob(workdir+"/*")

        # verify that exactly eight files + 1 source dir were produced
        self.assertEqual(14, len(files))

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
        self.assertEqual('three', data.entries[0].source['planet_css-id'])

    def test_spiderPlanet(self):
        config.load(configfile)
        spiderPlanet()
        self.verify_spiderPlanet()

    def test_spiderThreads(self):
        config.load(configfile.replace('config','threaded'))
        _PORT = config.parser.getint('Planet','test_port')

        log = []
        from SimpleHTTPServer import SimpleHTTPRequestHandler
        class TestRequestHandler(SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                log.append(args)

        from threading import Thread
        class TestServerThread(Thread):
          def __init__(self):
              self.ready = 0
              self.done = 0
              Thread.__init__(self)
          def run(self):
              from BaseHTTPServer import HTTPServer
              httpd = HTTPServer(('',_PORT), TestRequestHandler)
              self.ready = 1
              while not self.done:
                  httpd.handle_request()

        httpd = TestServerThread()
        httpd.start()
        while not httpd.ready:
            time.sleep(0.1)

        try:
            spiderPlanet()
        finally:
            httpd.done = 1
            import urllib
            urllib.urlopen('http://127.0.0.1:%d/' % _PORT).read()

        status = [int(rec[1]) for rec in log if str(rec[0]).startswith('GET ')]
        status.sort()
        self.assertEqual([200,200,200,200,404], status)

        self.verify_spiderPlanet()
