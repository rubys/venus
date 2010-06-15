#!/usr/bin/env python

import unittest
from planet import config

class ConfigTest(unittest.TestCase):
    def setUp(self):
        config.load('tests/data/config/basic.ini')

    # administrivia

    def test_template(self):
        self.assertEqual(['index.html.tmpl', 'atom.xml.tmpl'], 
            config.template_files())

    def test_feeds(self):
        feeds = config.subscriptions()
        feeds.sort()
        self.assertEqual(['feed1', 'feed2'], feeds)

    def test_feed(self):
        self.assertEqual('http://example.com/atom.xml', config.feed())
        self.assertEqual('atom', config.feedtype())

    # planet wide configuration

    def test_name(self):
        self.assertEqual('Test Configuration', config.name())

    def test_link(self):
        self.assertEqual('http://example.com/', config.link())

    def test_pubsubhubbub_hub(self):
        self.assertEqual('http://pubsubhubbub.appspot.com', config.pubsubhubbub_hub())

    # per template configuration

    def test_days_per_page(self):
        self.assertEqual(7, config.days_per_page('index.html.tmpl'))
        self.assertEqual(0, config.days_per_page('atom.xml.tmpl'))

    def test_items_per_page(self):
        self.assertEqual(50, config.items_per_page('index.html.tmpl'))
        self.assertEqual(50, config.items_per_page('atom.xml.tmpl'))

    def test_encoding(self):
        self.assertEqual('utf-8', config.encoding('index.html.tmpl'))
        self.assertEqual('utf-8', config.encoding('atom.xml.tmpl'))

    # dictionaries

    def test_feed_options(self):
        self.assertEqual('one', config.feed_options('feed1')['name'])
        self.assertEqual('two', config.feed_options('feed2')['name'])

    def test_template_options(self):
        option = config.template_options('index.html.tmpl')
        self.assertEqual('7',  option['days_per_page'])
        self.assertEqual('50', option['items_per_page'])

    def test_filters(self):
        self.assertEqual(['foo','bar'], config.filters('feed2'))
        self.assertEqual(['foo'], config.filters('feed1'))

    # ints

    def test_timeout(self):
        self.assertEqual(30,
            config.feed_timeout())


