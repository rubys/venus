#!/usr/bin/env python

import unittest, xml.dom.minidom
from planet import shell, config, logger

class FilterTests(unittest.TestCase):

    def test_coral_cdn(self):
        testfile = 'tests/data/filter/coral_cdn.xml'
        filter = 'coral_cdn_filter.py'

        output = shell.run(filter, open(testfile).read(), mode="filter")
        dom = xml.dom.minidom.parseString(output)
        imgsrc = dom.getElementsByTagName('img')[0].getAttribute('src')
        self.assertEqual('http://example.com.nyud.net:8080/foo.png', imgsrc)

    def test_excerpt_images(self):
        testfile = 'tests/data/filter/excerpt-images.xml'
        config.load('tests/data/filter/excerpt-images.ini')

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

    def test_xpath_filter(self):
        config.load('tests/data/filter/xpath-sifter.ini')
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

try:
    from subprocess import Popen, PIPE
    sed=Popen(['sed','--version'],stdout=PIPE,stderr=PIPE)
    sed.communicate()
    if sed.returncode != 0:
        logger.warn("sed is not available => can't test stripAd_yahoo")
        del FilterTests.test_stripAd_yahoo
except ImportError:
    logger.warn("Popen is not available => can't test filters")
    for method in dir(FilterTests):
        if method.startswith('test_'):  delattr(FilterTests,method)
