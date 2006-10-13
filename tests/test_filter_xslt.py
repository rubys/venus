#!/usr/bin/env python

import unittest, xml.dom.minidom
from planet import shell, config, logger

class XsltFilterTests(unittest.TestCase):

    def test_xslt_filter(self):
        config.load('tests/data/filter/translate.ini')
        testfile = 'tests/data/filter/category-one.xml'

        input = open(testfile).read()
        output = shell.run(config.filters()[0], input, mode="filter")
        dom = xml.dom.minidom.parseString(output)
        catterm = dom.getElementsByTagName('category')[0].getAttribute('term')
        self.assertEqual('OnE', catterm)

try:
    import libxslt
except:
    try:
        from subprocess import Popen, PIPE
    except ImportError:
        logger.warn("libxslt is not available => can't test xslt filters")
        del XsltFilterTests.test_xslt_filter
