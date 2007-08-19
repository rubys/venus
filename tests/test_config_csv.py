#!/usr/bin/env python

import os, shutil, unittest
from planet import config

workdir = os.path.join('tests', 'work', 'config', 'cache')

class ConfigCsvTest(unittest.TestCase):
    def setUp(self):
        config.load('tests/data/config/rlist-csv.ini')

    def tearDown(self):
        shutil.rmtree(workdir)
        os.removedirs(os.path.split(workdir)[0])

    # administrivia

    def test_feeds(self):
        feeds = config.subscriptions()
        feeds.sort()
        self.assertEqual(['feed1', 'feed2'], feeds)

    def test_filters(self):
        self.assertEqual(['foo','bar'], config.filters('feed2'))
        self.assertEqual(['foo'], config.filters('feed1'))
