#!/usr/bin/env python

import unittest
from planet.splice import splice

configfile = 'tests/data/splice/config.ini'

class SpliceTest(unittest.TestCase):

    def test_splice(self):
        doc = splice(configfile)
        self.assertEqual(8,len(doc.getElementsByTagName('entry')))
        self.assertEqual(2,len(doc.getElementsByTagName('planet:subscription')))
        self.assertEqual(10,len(doc.getElementsByTagName('planet:name')))

        self.assertEqual('test planet',
            doc.getElementsByTagName('title')[0].firstChild.nodeValue)
