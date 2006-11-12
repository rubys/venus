#!/usr/bin/env python

import unittest
from planet import config
from os.path import split

class ThemesTest(unittest.TestCase):
    def setUp(self):
        config.load('tests/data/config/themed.ini')

    # template directories

    def test_template_directories(self):
        self.assertEqual(['foo', 'bar', 'asf', 'config', 'common'],
            [split(dir)[1] for dir in config.template_directories()])

    # administrivia

    def test_template(self):
        self.assertEqual(1, len([1 for file in config.template_files()
            if file == 'index.html.xslt']))

    def test_feeds(self):
        feeds = config.subscriptions()
        feeds.sort()
        self.assertEqual(['feed1', 'feed2'], feeds)

    # planet wide configuration

    def test_name(self):
        self.assertEqual('Test Configuration', config.name())

    def test_link(self):
        self.assertEqual('', config.link())

    # per template configuration

    def test_days_per_page(self):
        self.assertEqual(7, config.days_per_page('index.html.xslt'))
        self.assertEqual(0, config.days_per_page('atom.xml.xslt'))

    def test_items_per_page(self):
        self.assertEqual(50, config.items_per_page('index.html.xslt'))
        self.assertEqual(50, config.items_per_page('atom.xml.xslt'))

    def test_encoding(self):
        self.assertEqual('utf-8', config.encoding('index.html.xslt'))
        self.assertEqual('utf-8', config.encoding('atom.xml.xslt'))

    # dictionaries

    def test_feed_options(self):
        self.assertEqual('one', config.feed_options('feed1')['name'])
        self.assertEqual('two', config.feed_options('feed2')['name'])

    def test_template_options(self):
        option = config.template_options('index.html.xslt')
        self.assertEqual('7',  option['days_per_page'])
        self.assertEqual('50', option['items_per_page'])
