#!/usr/bin/env python
# coding=utf-8

import sys
import unittest
import xml.dom.minidom

import pytest

from planet import config, shell

try:
    import libxml2

    libxml2_available = True
except ImportError:
    libxml2_available = False


class FilterTests(unittest.TestCase):
    def test_coral_cdn(self):
        testfile = 'tests/data/filter/coral_cdn.xml'
        the_filter = 'coral_cdn_filter.py'
        with open(testfile) as fp:
            output = shell.run(the_filter, fp.read(), mode="filter")
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
        with open(testfile) as fp:
            output = fp.read()
        for each_filter in config.filters():
            output = shell.run(each_filter, output, mode="filter")

        dom = xml.dom.minidom.parseString(output)
        excerpt = dom.getElementsByTagName('planet:excerpt')[0]
        anchors = excerpt.getElementsByTagName('a')
        hrefs = [a.getAttribute('href') for a in anchors]
        texts = [a.lastChild.nodeValue for a in anchors]

        self.assertEqual(['inner', 'outer1', 'outer2'], hrefs)
        self.assertEqual(['bar', 'bar', '<img>'], texts)

    def test_excerpt_lorem_ipsum(self):
        testfile = 'tests/data/filter/excerpt-lorem-ipsum.xml'
        config.load('tests/data/filter/excerpt-lorem-ipsum.ini')

        with open(testfile) as fp:
            output = fp.read()
        for each_filter in config.filters():
            output = shell.run(each_filter, output, mode="filter")

        dom = xml.dom.minidom.parseString(output)
        excerpt = dom.getElementsByTagName('planet:excerpt')[0]
        self.assertEqual(u'Lorem ipsum dolor sit amet, consectetuer ' +
                         u'adipiscing elit. Nullam velit. Vivamus tincidunt, erat ' +
                         u'in \u2026', excerpt.firstChild.firstChild.nodeValue)

    def test_excerpt_lorem_ipsum_summary(self):
        testfile = 'tests/data/filter/excerpt-lorem-ipsum.xml'
        config.load('tests/data/filter/excerpt-lorem-ipsum.ini')
        config.parser.set('excerpt.py', 'target', 'atom:summary')

        with open(testfile) as fp:
            output = fp.read()
        for each_filter in config.filters():
            output = shell.run(each_filter, output, mode="filter")

        dom = xml.dom.minidom.parseString(output)
        excerpt = dom.getElementsByTagName('summary')[0]
        self.assertEqual(u'Lorem ipsum dolor sit amet, consectetuer ' +
                         u'adipiscing elit. Nullam velit. Vivamus tincidunt, erat ' +
                         u'in \u2026', excerpt.firstChild.firstChild.nodeValue)

    @pytest.mark.skipif(sys.platform == 'win32', reason="sed is not available on windows")
    def test_stripAd_yahoo(self):
        testfile = 'tests/data/filter/stripAd-yahoo.xml'
        config.load('tests/data/filter/stripAd-yahoo.ini')

        with open(testfile) as fp:
            output = fp.read()
        for each_filter in config.filters():
            output = shell.run(each_filter, output, mode="filter")

        dom = xml.dom.minidom.parseString(output)
        excerpt = dom.getElementsByTagName('content')[0]
        self.assertEqual(u'before--after',
                         excerpt.firstChild.firstChild.nodeValue)

    @pytest.mark.skipif(not libxml2_available, reason="libxml2 is not installed")
    def test_xpath_filter1(self):
        config.load('tests/data/filter/xpath-sifter.ini')
        self.verify_xpath()

    @pytest.mark.skipif(not libxml2_available, reason="libxml2 is not installed")
    def test_xpath_filter2(self):
        config.load('tests/data/filter/xpath-sifter2.ini')
        self.verify_xpath()

    def verify_xpath(self):
        testfile = 'tests/data/filter/category-one.xml'

        with open(testfile) as fp:
            output = fp.read()
        for each_filter in config.filters():
            output = shell.run(each_filter, output, mode="filter")

        self.assertEqual('', output)

        testfile = 'tests/data/filter/category-two.xml'

        with open(testfile) as fp:
            output = fp.read()
        for each_filter in config.filters():
            output = shell.run(each_filter, output, mode="filter")

        self.assertNotEqual('', output)

    def test_regexp_filter(self):
        config.load('tests/data/filter/regexp-sifter.ini')

        testfile = 'tests/data/filter/category-one.xml'

        with open(testfile) as fp:
            output = fp.read()
        for each_filter in config.filters():
            output = shell.run(each_filter, output, mode="filter")

        self.assertEqual('', output)

        testfile = 'tests/data/filter/category-two.xml'

        with open(testfile) as fp:
            output = fp.read()
        for each_filter in config.filters():
            output = shell.run(each_filter, output, mode="filter")

        self.assertNotEqual('', output)

    def test_regexp_filter2(self):
        config.load('tests/data/filter/regexp-sifter2.ini')

        testfile = 'tests/data/filter/category-one.xml'

        with open(testfile) as fp:
            output = fp.read()
        for each_filter in config.filters():
            output = shell.run(each_filter, output, mode="filter")

        self.assertNotEqual('', output)

        testfile = 'tests/data/filter/category-two.xml'

        with open(testfile) as fp:
            output = fp.read()
        for each_filter in config.filters():
            output = shell.run(each_filter, output, mode="filter")

        self.assertEqual('', output)

    def test_xhtml2html_filter(self):
        testfile = 'tests/data/filter/index.html'
        the_filter = 'xhtml2html.plugin?quote_attr_values=True'
        with open(testfile) as fp:
            output = shell.run(the_filter, fp.read(), mode="filter")
        self.assertTrue(output.find('/>') < 0)
        self.assertTrue(output.find('</script>') >= 0)
