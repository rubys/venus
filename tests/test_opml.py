#!/usr/bin/env python

import unittest
from planet.opml import opml2config
from ConfigParser import ConfigParser

class OpmlTest(unittest.TestCase):
    """
    Test the opml2config function
    """

    def setUp(self):
        self.config = ConfigParser()

    #
    # Element
    #

    def test_outline_element(self):
        opml2config('''<outline type="rss"
                                xmlUrl="http://example.com/feed.xml"
                                text="sample feed"/>''', self.config)
        self.assertEqual('sample feed',
           self.config.get("http://example.com/feed.xml", 'name'))

    def test_wrong_element(self):
        opml2config('''<feed    type="rss"
                                xmlUrl="http://example.com/feed.xml"
                                text="sample feed"/>''', self.config)
        self.assertFalse(self.config.has_section("http://example.com/feed.xml"))

    def test_illformed_xml_before(self):
        opml2config('''<bad stuff before>
                       <outline type="rss"
                                xmlUrl="http://example.com/feed.xml"
                                text="sample feed"/>''', self.config)
        self.assertEqual('sample feed',
           self.config.get("http://example.com/feed.xml", 'name'))

    def test_illformed_xml_after(self):
        opml2config('''<outline type="rss"
                                xmlUrl="http://example.com/feed.xml"
                                text="sample feed"/>
                       <bad stuff after>''', self.config)
        self.assertEqual('sample feed',
           self.config.get("http://example.com/feed.xml", 'name'))

    #
    # Type
    #

    def test_type_missing(self):
        opml2config('''<outline
                                xmlUrl="http://example.com/feed.xml"
                                text="sample feed"/>''', self.config)
        self.assertEqual('sample feed',
           self.config.get("http://example.com/feed.xml", 'name'))

    def test_type_uppercase(self):
        opml2config('''<outline type="RSS"
                                xmlUrl="http://example.com/feed.xml"
                                text="sample feed"/>''', self.config)
        self.assertEqual('sample feed',
           self.config.get("http://example.com/feed.xml", 'name'))

    def test_type_atom(self):
        opml2config('''<outline type="atom"
                                xmlUrl="http://example.com/feed.xml"
                                text="sample feed"/>''', self.config)
        self.assertEqual('sample feed',
           self.config.get("http://example.com/feed.xml", 'name'))

    def test_wrong_type(self):
        opml2config('''<outline type="other"
                                xmlUrl="http://example.com/feed.xml"
                                text="sample feed"/>''', self.config)
        self.assertFalse(self.config.has_section("http://example.com/feed.xml"))

    def test_WordPress_link_manager(self):
        # http://www.wasab.dk/morten/blog/archives/2006/10/22/wp-venus
        opml2config('''<outline type="link"
                                xmlUrl="http://example.com/feed.xml"
                                text="sample feed"/>''', self.config)
        self.assertEqual('sample feed',
           self.config.get("http://example.com/feed.xml", 'name'))

    #
    # xmlUrl
    #

    def test_xmlurl_wrong_case(self):
        opml2config('''<outline type="rss"
                                xmlurl="http://example.com/feed.xml"
                                text="sample feed"/>''', self.config)
        self.assertEqual('sample feed',
           self.config.get("http://example.com/feed.xml", 'name'))

    def test_missing_xmlUrl(self):
        opml2config('''<outline type="rss"
                                text="sample feed"/>''', self.config)
        self.assertFalse(self.config.has_section("http://example.com/feed.xml"))

    def test_blank_xmlUrl(self):
        opml2config('''<outline type="rss"
                                xmlUrl=""
                                text="sample feed"/>''', self.config)
        self.assertFalse(self.config.has_section(""))

    #
    # text
    #

    def test_title_attribute(self):
        opml2config('''<outline type="rss"
                                xmlUrl="http://example.com/feed.xml"
                                title="sample feed"/>''', self.config)
        self.assertEqual('sample feed',
           self.config.get("http://example.com/feed.xml", 'name'))

    def test_missing_text(self):
        opml2config('''<outline type="rss"
                                xmlUrl="http://example.com/feed.xml"
                                />''', self.config)
        self.assertFalse(self.config.has_section("http://example.com/feed.xml"))

    def test_blank_text_no_title(self):
        opml2config('''<outline type="rss"
                                xmlUrl="http://example.com/feed.xml"
                                text=""/>''', self.config)
        self.assertFalse(self.config.has_section("http://example.com/feed.xml"))

    def test_blank_text_with_title(self):
        opml2config('''<outline type="rss"
                                xmlUrl="http://example.com/feed.xml"
                                text=""
                                title="sample feed"/>''', self.config)
        self.assertEqual('sample feed',
           self.config.get("http://example.com/feed.xml", 'name'))

    def test_blank_text_blank_title(self):
        opml2config('''<outline type="rss"
                                xmlUrl="http://example.com/feed.xml"
                                text=""
                                title=""/>''', self.config)
        self.assertFalse(self.config.has_section("http://example.com/feed.xml"))

    def test_text_utf8(self):
        opml2config('''<outline type="rss"
                                xmlUrl="http://example.com/feed.xml"
                                text="Se\xc3\xb1or Frog\xe2\x80\x99s"/>''',
                    self.config)
        self.assertEqual('Se\xc3\xb1or Frog\xe2\x80\x99s',
           self.config.get("http://example.com/feed.xml", 'name'))

    def test_text_win_1252(self):
        opml2config('''<outline type="rss"
                                xmlUrl="http://example.com/feed.xml"
                                text="Se\xf1or Frog\x92s"/>''', self.config)
        self.assertEqual('Se\xc3\xb1or Frog\xe2\x80\x99s',
           self.config.get("http://example.com/feed.xml", 'name'))

    def test_text_entity(self):
        opml2config('''<outline type="rss"
                                xmlUrl="http://example.com/feed.xml"
                                text="Se&ntilde;or Frog&rsquo;s"/>''', self.config)
        self.assertEqual('Se\xc3\xb1or Frog\xe2\x80\x99s',
           self.config.get("http://example.com/feed.xml", 'name'))

    def test_text_double_escaped(self):
        opml2config('''<outline type="rss"
                                xmlUrl="http://example.com/feed.xml"
                                text="Se&amp;ntilde;or Frog&amp;rsquo;s"/>''', self.config)
        self.assertEqual('Se\xc3\xb1or Frog\xe2\x80\x99s',
           self.config.get("http://example.com/feed.xml", 'name'))

if __name__ == '__main__':
    unittest.main()
