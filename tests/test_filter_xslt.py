#!/usr/bin/env python
# coding=utf-8

import unittest
import xml.dom.minidom

from planet import config, logger, shell


class XsltFilterTests(unittest.TestCase):
    def test_xslt_filter(self):
        config.load('tests/data/filter/translate.ini')
        testfile = 'tests/data/filter/category-one.xml'

        with open(testfile) as fp:
            input_ = fp.read()
        output = shell.run(config.filters()[0], input_, mode="filter")
        dom = xml.dom.minidom.parseString(output)
        catterm = dom.getElementsByTagName('category')[0].getAttribute('term')
        self.assertEqual('OnE', catterm)

    def test_addsearch_filter(self):
        testfile = 'tests/data/filter/index.html'
        the_filter = 'addsearch.xslt'
        with open(testfile) as fp:
            output = shell.run(the_filter, fp.read(), mode="filter")
        self.assertTrue(output.find('<h2>Search</h2>') >= 0)
        self.assertTrue(output.find('<form><input name="q"/></form>') >= 0)
        self.assertTrue(output.find(' href="http://planet.intertwingly.net/opensearchdescription.xml"') >= 0)
        self.assertTrue(output.find('</script>') >= 0)


try:
    import libxslt
except ImportError:
    try:
        from subprocess import Popen, PIPE

        xsltproc = Popen(['xsltproc', '--version'], stdout=PIPE, stderr=PIPE)
        xsltproc.communicate()
        if xsltproc.returncode != 0:
            raise ImportError
    except ImportError:
        logger.warn("libxslt is not available => can't test xslt filters")
        del XsltFilterTests.test_xslt_filter
        del XsltFilterTests.test_addsearch_filter
