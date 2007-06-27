#!/usr/bin/env python

import unittest, xml.dom.minidom
from planet import shell, config, logger

class FilterTests(unittest.TestCase):

    def test_coral_cdn(self):
        testfile = 'tests/data/filter/coral_cdn.xml'
        filter = 'coral_cdn_filter.py'

        output = shell.run(filter, open(testfile).read(), mode="filter")
        dom = xml.dom.minidom.parseString(output)
        imgsrcs = [img.getAttribute('src') for img in dom.getElementsByTagName('img')]
        self.assertEqual('http://example.com.nyud.net:8080/foo.png', imgsrcs[0])
        self.assertEqual('http://example.com.1234.nyud.net:8080/foo.png', imgsrcs[1])
        self.assertEqual('http://u:p@example.com.nyud.net:8080/foo.png', imgsrcs[2])
        self.assertEqual('http://u:p@example.com.1234.nyud.net:8080/foo.png', imgsrcs[3])

    def test_excerpt_images1(self):
        config.load('tests/data/filter/excerpt-images.ini')
        self.verify_images()

    def test_excerpt_images2(self):
        config.load('tests/data/filter/excerpt-images2.ini')
        self.verify_images()

    def verify_images(self):
        testfile = 'tests/data/filter/excerpt-images.xml'
        output = open(testfile).read()
        for filter in config.filters():
            output = shell.run(filter, output, mode="filter")

        dom = xml.dom.minidom.parseString(output)
        excerpt = dom.getElementsByTagName('planet:excerpt')[0]
        anchors = excerpt.getElementsByTagName('a')
        hrefs = [a.getAttribute('href') for a in anchors]
        texts = [a.lastChild.nodeValue for a in anchors]

        self.assertEqual(['inner','outer1','outer2'], hrefs)
        self.assertEqual(['bar','bar','<img>'], texts)

    def test_excerpt_lorem_ipsum(self):
        testfile = 'tests/data/filter/excerpt-lorem-ipsum.xml'
        config.load('tests/data/filter/excerpt-lorem-ipsum.ini')

        output = open(testfile).read()
        for filter in config.filters():
            output = shell.run(filter, output, mode="filter")

        dom = xml.dom.minidom.parseString(output)
        excerpt = dom.getElementsByTagName('planet:excerpt')[0]
        self.assertEqual(u'Lorem ipsum dolor sit amet, consectetuer ' +
            u'adipiscing elit. Nullam velit. Vivamus tincidunt, erat ' +
            u'in \u2026', excerpt.firstChild.firstChild.nodeValue)

    def test_excerpt_lorem_ipsum_summary(self):
        testfile = 'tests/data/filter/excerpt-lorem-ipsum.xml'
        config.load('tests/data/filter/excerpt-lorem-ipsum.ini')
        config.parser.set('excerpt.py', 'target', 'atom:summary')

        output = open(testfile).read()
        for filter in config.filters():
            output = shell.run(filter, output, mode="filter")

        dom = xml.dom.minidom.parseString(output)
        excerpt = dom.getElementsByTagName('summary')[0]
        self.assertEqual(u'Lorem ipsum dolor sit amet, consectetuer ' +
            u'adipiscing elit. Nullam velit. Vivamus tincidunt, erat ' +
            u'in \u2026', excerpt.firstChild.firstChild.nodeValue)

    def test_stripAd_yahoo(self):
        testfile = 'tests/data/filter/stripAd-yahoo.xml'
        config.load('tests/data/filter/stripAd-yahoo.ini')

        output = open(testfile).read()
        for filter in config.filters():
            output = shell.run(filter, output, mode="filter")

        dom = xml.dom.minidom.parseString(output)
        excerpt = dom.getElementsByTagName('content')[0]
        self.assertEqual(u'before--after',
            excerpt.firstChild.firstChild.nodeValue)

    def test_xpath_filter1(self):
        config.load('tests/data/filter/xpath-sifter.ini')
        self.verify_xpath()

    def test_xpath_filter2(self):
        config.load('tests/data/filter/xpath-sifter2.ini')
        self.verify_xpath()

    def verify_xpath(self):
        testfile = 'tests/data/filter/category-one.xml'

        output = open(testfile).read()
        for filter in config.filters():
            output = shell.run(filter, output, mode="filter")

        self.assertEqual('', output)

        testfile = 'tests/data/filter/category-two.xml'

        output = open(testfile).read()
        for filter in config.filters():
            output = shell.run(filter, output, mode="filter")

        self.assertNotEqual('', output)

    def test_regexp_filter(self):
        config.load('tests/data/filter/regexp-sifter.ini')

        testfile = 'tests/data/filter/category-one.xml'

        output = open(testfile).read()
        for filter in config.filters():
            output = shell.run(filter, output, mode="filter")

        self.assertEqual('', output)

        testfile = 'tests/data/filter/category-two.xml'

        output = open(testfile).read()
        for filter in config.filters():
            output = shell.run(filter, output, mode="filter")

        self.assertNotEqual('', output)

    def test_regexp_filter2(self):
        config.load('tests/data/filter/regexp-sifter2.ini')

        testfile = 'tests/data/filter/category-one.xml'

        output = open(testfile).read()
        for filter in config.filters():
            output = shell.run(filter, output, mode="filter")

        self.assertNotEqual('', output)

        testfile = 'tests/data/filter/category-two.xml'

        output = open(testfile).read()
        for filter in config.filters():
            output = shell.run(filter, output, mode="filter")

        self.assertEqual('', output)

    def test_xhtml2html_filter(self):
        testfile = 'tests/data/filter/index.html'
        filter = 'xhtml2html.plugin?quote_attr_values=True'
        output = shell.run(filter, open(testfile).read(), mode="filter")
        self.assertTrue(output.find('/>')<0)
        self.assertTrue(output.find('</script>')>=0)

try:
    from subprocess import Popen, PIPE

    _no_sed = True
    if _no_sed:
        try:
            # Python 2.5 bug 1704790 workaround (alas, Unix only)
            import commands
            if commands.getstatusoutput('sed --version')[0]==0: _no_sed = False 
        except:
            pass

    if _no_sed:
        try:
            sed = Popen(['sed','--version'],stdout=PIPE,stderr=PIPE)
            sed.communicate()
            if sed.returncode == 0: _no_sed = False
        except WindowsError:
            pass

    if _no_sed:
        logger.warn("sed is not available => can't test stripAd_yahoo")
        del FilterTests.test_stripAd_yahoo      

    try:
        import libxml2
    except:
        logger.warn("libxml2 is not available => can't test xpath_sifter")
        del FilterTests.test_xpath_filter1
        del FilterTests.test_xpath_filter2

except ImportError:
    logger.warn("Popen is not available => can't test standard filters")
    for method in dir(FilterTests):
        if method.startswith('test_'):  delattr(FilterTests,method)
