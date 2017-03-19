#!/usr/bin/env python
# coding=utf-8

from planet import config
from test_config_csv import ConfigCsvTest


class SubConfigTest(ConfigCsvTest):
    def setUp(self):
        config.load('tests/data/config/rlist-config.ini')
