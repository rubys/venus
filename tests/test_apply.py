#!/usr/bin/env python

import unittest, os, shutil
from planet import config, splice
from xml.dom import minidom

workdir = 'tests/work/apply'
configfile = 'tests/data/apply/config.ini'
testfeed = 'tests/data/apply/feed.xml'

class ApplyTest(unittest.TestCase):
    def setUp(self):
        try:
             os.makedirs(workdir)
        except:
             self.tearDown()
             os.makedirs(workdir)
    
    def tearDown(self):
        shutil.rmtree(workdir)
        os.removedirs(os.path.split(workdir)[0])

    def test_apply(self):
        testfile = open(testfeed)
        feeddata = testfile.read()
        testfile.close()

        config.load(configfile)
        splice.apply(feeddata)

        # verify that selected files are there
        for file in ['index.html', 'default.css', 'images/foaf.png']:
            path = os.path.join(workdir, file)
            self.assertTrue(os.path.exists(path))
            self.assertTrue(os.stat(path).st_size > 0)

        # verify that index.html is well formed, has content, and xml:lang
        html = open(os.path.join(workdir, 'index.html'))
        doc = minidom.parse(html)
        list = []
        content = lang = 0
        for div in doc.getElementsByTagName('div'):
            if div.getAttribute('class') != 'content': continue
            content += 1
            if div.getAttribute('xml:lang') == 'en-us': lang += 1
        html.close()
        self.assertEqual(3, lang)
        self.assertEqual(12, content)
