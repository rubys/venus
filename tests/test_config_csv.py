#!/usr/bin/env python

import unittest
from planet import config

class ConfigCsvTest(unittest.TestCase):
    def setUp(self):
        config.load('tests/data/config/rlist-csv.ini')

    # administrivia

    def test_feeds(self):
        feeds = config.subscriptions()
        feeds.sort()
        self.assertEqual(['feed1', 'feed2'], feeds)

    def test_filters(self):
        self.assertEqual(['foo','bar'], config.filters('feed2'))
        self.assertEqual(['foo'], config.filters('feed1'))
