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

    def test_addsearch_filter(self):
        testfile = 'tests/data/filter/index.html'
        filter = 'addsearch.xslt'
        output = shell.run(filter, open(testfile).read(), mode="filter")
        self.assertTrue(output.find('<h2>Search</h2>')>=0)
        self.assertTrue(output.find('<form><input name="q"/></form>')>=0)
        self.assertTrue(output.find(' href="http://planet.intertwingly.net/opensearchdescription.xml"')>=0)
        self.assertTrue(output.find('</script>')>=0)

try:
    import libxslt
except:
    try:
        try:
            # Python 2.5 bug 1704790 workaround (alas, Unix only)
            import commands
            if commands.getstatusoutput('xsltproc --version')[0] != 0:
                raise ImportError
        except:
            from subprocess import Popen, PIPE
            xsltproc=Popen(['xsltproc','--version'],stdout=PIPE,stderr=PIPE)
            xsltproc.communicate()
            if xsltproc.returncode != 0: raise ImportError
    except:
        logger.warn("libxslt is not available => can't test xslt filters")
        del XsltFilterTests.test_xslt_filter
        del XsltFilterTests.test_addsearch_filter
