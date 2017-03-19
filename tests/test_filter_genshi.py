#!/usr/bin/env python
# coding=utf-8

import unittest

from planet import logger, shell


class GenshiFilterTests(unittest.TestCase):
    def test_addsearch_filter(self):
        testfile = 'tests/data/filter/index.html'
        the_filter = 'addsearch.genshi'
        with open(testfile) as fp:
            output = shell.run(the_filter, fp.read(), mode="filter")
        self.assertTrue(output.find('<h2>Search</h2>') >= 0)
        self.assertTrue(output.find('<form><input name="q"/></form>') >= 0)
        self.assertTrue(output.find(' href="http://planet.intertwingly.net/opensearchdescription.xml"') >= 0)
        self.assertTrue(output.find('</script>') >= 0)


try:
    import genshi
except ImportError:
    logger.warn("Genshi is not available => can't test genshi filters")
    for method in dir(GenshiFilterTests):
        if method.startswith('test_'):
            delattr(GenshiFilterTests, method)
