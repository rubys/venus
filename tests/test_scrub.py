#!/usr/bin/env python

import unittest, StringIO, time
from copy import deepcopy
from planet.scrub import scrub
from planet import feedparser, config

feed = '''
<feed xmlns='http://www.w3.org/2005/Atom' xml:base="http://example.com/">
  <author><name>F&amp;ouml;o</name></author>
  <entry xml:lang="en">
    <id>ignoreme</id>
    <author><name>F&amp;ouml;o</name></author>
    <updated>%d-12-31T23:59:59Z</updated>
    <title>F&amp;ouml;o</title>
    <summary>F&amp;ouml;o</summary>
    <content>F&amp;ouml;o</content>
    <link href="http://example.com/entry/1/"/>
    <source>
      <link href="http://example.com/feed/"/>
      <author><name>F&amp;ouml;o</name></author>
    </source>
  </entry>
</feed>
''' % (time.gmtime()[0] + 1)

configData = '''
[testfeed]
ignore_in_feed = 
future_dates = 

name_type = html
title_type = html
summary_type = html
content_type = html
'''

class ScrubTest(unittest.TestCase):

    def test_scrub_ignore(self):
        base = feedparser.parse(feed)

        self.assertTrue(base.entries[0].has_key('author'))
        self.assertTrue(base.entries[0].has_key('author_detail'))
        self.assertTrue(base.entries[0].has_key('id'))
        self.assertTrue(base.entries[0].has_key('updated'))
        self.assertTrue(base.entries[0].has_key('updated_parsed'))
        self.assertTrue(base.entries[0].summary_detail.has_key('language'))

        config.parser.readfp(StringIO.StringIO(configData))
        config.parser.set('testfeed', 'ignore_in_feed',
          'author id updated xml:lang')
        data = deepcopy(base)
        scrub('testfeed', data)

        self.assertFalse(data.entries[0].has_key('author'))
        self.assertFalse(data.entries[0].has_key('author_detail'))
        self.assertFalse(data.entries[0].has_key('id'))
        self.assertFalse(data.entries[0].has_key('updated'))
        self.assertFalse(data.entries[0].has_key('updated_parsed'))
        self.assertFalse(data.entries[0].summary_detail.has_key('language'))

    def test_scrub_type(self):
        base = feedparser.parse(feed)

        self.assertEqual('F&ouml;o', base.feed.author_detail.name)

        config.parser.readfp(StringIO.StringIO(configData))
        data = deepcopy(base)
        scrub('testfeed', data)

        self.assertEqual('F\xc3\xb6o', data.feed.author_detail.name)
        self.assertEqual('F\xc3\xb6o', data.entries[0].author_detail.name)
        self.assertEqual('F\xc3\xb6o', data.entries[0].source.author_detail.name)

        self.assertEqual('text/html', data.entries[0].title_detail.type)
        self.assertEqual('text/html', data.entries[0].summary_detail.type)
        self.assertEqual('text/html', data.entries[0].content[0].type)

    def test_scrub_future(self):
        base = feedparser.parse(feed)
        self.assertEqual(1, len(base.entries))
        self.assertTrue(base.entries[0].has_key('updated'))

        config.parser.readfp(StringIO.StringIO(configData))
        config.parser.set('testfeed', 'future_dates', 'ignore_date')
        data = deepcopy(base)
        scrub('testfeed', data)
        self.assertFalse(data.entries[0].has_key('updated'))

        config.parser.set('testfeed', 'future_dates', 'ignore_entry')
        data = deepcopy(base)
        scrub('testfeed', data)
        self.assertEqual(0, len(data.entries))

    def test_scrub_xmlbase(self):
        base = feedparser.parse(feed)
        self.assertEqual('http://example.com/',
             base.entries[0].title_detail.base)

        config.parser.readfp(StringIO.StringIO(configData))
        config.parser.set('testfeed', 'xml_base', 'feed_alternate')
        data = deepcopy(base)
        scrub('testfeed', data)
        self.assertEqual('http://example.com/feed/',
             data.entries[0].title_detail.base)

        config.parser.set('testfeed', 'xml_base', 'entry_alternate')
        data = deepcopy(base)
        scrub('testfeed', data)
        self.assertEqual('http://example.com/entry/1/',
             data.entries[0].title_detail.base)

        config.parser.set('testfeed', 'xml_base', 'base/')
        data = deepcopy(base)
        scrub('testfeed', data)
        self.assertEqual('http://example.com/base/',
             data.entries[0].title_detail.base)

        config.parser.set('testfeed', 'xml_base', 'http://example.org/data/')
        data = deepcopy(base)
        scrub('testfeed', data)
        self.assertEqual('http://example.org/data/',
             data.entries[0].title_detail.base)
