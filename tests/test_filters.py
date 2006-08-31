#!/usr/bin/env python

import unittest, xml.dom.minidom
from planet import shell

testfile = 'tests/data/filter/coral_cdn.xml'
filter = 'coral_cdn_filter.py'

class FilterTests(unittest.TestCase):

    def test_coral_cdn(self):
        output = shell.run(filter, open(testfile).read(), mode="filter")
        dom = xml.dom.minidom.parseString(output)
        imgsrc = dom.getElementsByTagName('img')[0].getAttribute('src')
        self.assertEqual('http://example.com.nyud.net:8080/foo.png', imgsrc)
