#!/usr/bin/env python

import unittest
from planet.splice import splice

configfile = 'tests/data/splice/config.ini'

class SpliceTest(unittest.TestCase):

    def test_splice(self):
        doc = splice(configfile)
        self.assertEqual(12,len(doc.getElementsByTagName('entry')))
        self.assertEqual(4,len(doc.getElementsByTagName('planet:source')))
        self.assertEqual(16,len(doc.getElementsByTagName('planet:name')))

        self.assertEqual('test planet',
            doc.getElementsByTagName('title')[0].firstChild.nodeValue)
