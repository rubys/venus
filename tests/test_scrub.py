#!/usr/bin/env python

import unittest, StringIO
from planet.spider import scrub
from planet import feedparser, config

feed = '''
<feed xmlns='http://www.w3.org/2005/Atom'>
  <author><name>F&amp;ouml;o</name></author>
  <entry xml:lang="en">
    <id>ignoreme</id>
    <author><name>F&amp;ouml;o</name></author>
    <updated>2000-01-01T00:00:00Z</updated>
    <title>F&amp;ouml;o</title>
    <summary>F&amp;ouml;o</summary>
    <content>F&amp;ouml;o</content>
    <source>
      <author><name>F&amp;ouml;o</name></author>
    </source>
  </entry>
</feed>
'''

configData = '''
[testfeed]
ignore_in_feed = id updated xml:lang
name_type = html
title_type = html
summary_type = html
content_type = html
'''

class ScrubTest(unittest.TestCase):

    def test_scrub(self):
        data = feedparser.parse(feed)
        config.parser.readfp(StringIO.StringIO(configData))

        self.assertEqual('F&ouml;o', data.feed.author_detail.name)
        self.assertTrue(data.entries[0].has_key('id'))
        self.assertTrue(data.entries[0].has_key('updated'))
        self.assertTrue(data.entries[0].has_key('updated_parsed'))
        self.assertTrue(data.entries[0].summary_detail.has_key('language'))

        scrub('testfeed', data)

        self.assertFalse(data.entries[0].has_key('id'))
        self.assertFalse(data.entries[0].has_key('updated'))
        self.assertFalse(data.entries[0].has_key('updated_parsed'))
        self.assertFalse(data.entries[0].summary_detail.has_key('language'))

        self.assertEqual('F\xc3\xb6o', data.feed.author_detail.name)
        self.assertEqual('F\xc3\xb6o', data.entries[0].author_detail.name)
        self.assertEqual('F\xc3\xb6o', data.entries[0].source.author_detail.name)

        self.assertEqual('text/html', data.entries[0].title_detail.type)
        self.assertEqual('text/html', data.entries[0].summary_detail.type)
        self.assertEqual('text/html', data.entries[0].content[0].type)

