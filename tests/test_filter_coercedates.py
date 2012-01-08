#!/usr/bin/env python

import unittest, os, glob, calendar, shutil, time
from planet.spider import filename, spiderPlanet, writeCache
from planet import feedparser, config
import planet

workdir = 'tests/work/coercedates/cache'
testfeed = 'tests/data/filter/coercedates/%s.xml'
configfile = 'tests/data/filter/coercedates/config.ini'

class CoerceDatesTest(unittest.TestCase):
    def setUp(self):
        # silence errors
        self.original_logger = planet.logger
        # planet.getLogger('CRITICAL',None)

        try:
             os.makedirs(workdir)
        except:
             self.tearDown()
             os.makedirs(workdir)
    
    def tearDown(self):
        shutil.rmtree(workdir)
        os.removedirs(os.path.split(workdir)[0])
        planet.logger = self.original_logger

    def spiderFeed(self, feed_uri):
        feed_info = feedparser.parse('<feed/>')
        data = feedparser.parse(feed_uri)
        writeCache(feed_uri, feed_info, data)

    # no expected_date means we don't know what it should be yet
    def verify_date(self, id, expected_date = None):

        file = os.path.join(workdir, id)

        # verify that the file exists
        self.assertTrue(os.path.exists(file), msg=file);

        data = feedparser.parse(file)

        # verify published & updated dates are in sync and match expected

        self.assertEqual(data.entries[0].updated,
                         data.entries[0].published)

        # verify mtime is in sync
        self.assertEqual(time.gmtime(os.stat(file).st_mtime),
                         data.entries[0].updated_parsed)
        self.assertEqual(time.gmtime(os.stat(file).st_mtime),
                         data.entries[0].published_parsed)

        # verify meet hardcoded expectations
        if expected_date is not None:
            self.assertEqual(expected_date, 
                             data.entries[0].updated)

        return data.entries[0].updated

    def test_coerce_rss(self):
        config.load(configfile)

        # load first version of RSS
        self.spiderFeed(testfeed % 'a-rss-1')

        rss_no_date_expected = self.verify_date('fake.url.example.com,rss-no-date')
        self.verify_date('fake.url.example.com,rss-changing-date', 
                         u'2011-12-01T11:00:00Z')

        # parse updated RSS feed
        self.spiderFeed(testfeed % 'a-rss-2')
        
        # verify dates haven't changed
        self.verify_date('fake.url.example.com,rss-no-date',
                         rss_no_date_expected)
        self.verify_date('fake.url.example.com,rss-changing-date', 
                         u'2011-12-01T11:00:00Z')
        
    def test_coerce_atom(self):
        config.load(configfile)

        # load first version of Atom
        self.spiderFeed(testfeed % 'b-atom-1')

        atom_no_date_expected = self.verify_date('fake.url.example.com,atom-no-date')
        self.verify_date('fake.url.example.com,atom-changing-published', 
                         u'2011-12-08T02:02:28Z')
        self.verify_date('fake.url.example.com,atom-changing-updated', 
                         u'2011-11-09T00:00:28Z')
        self.verify_date('fake.url.example.com,atom-update-before-pub', 
                         u'2011-11-11T11:11:11Z')

        # parse updated Atom feed
        self.spiderFeed(testfeed % 'b-atom-2')

        # verify dates haven't changed
        self.verify_date('fake.url.example.com,atom-no-date',
                         atom_no_date_expected)
        self.verify_date('fake.url.example.com,atom-changing-published', 
                         u'2011-12-08T02:02:28Z')
        self.verify_date('fake.url.example.com,atom-changing-updated', 
                         u'2011-11-09T00:00:28Z')
        self.verify_date('fake.url.example.com,atom-update-before-pub', 
                         u'2011-11-11T11:11:11Z')
