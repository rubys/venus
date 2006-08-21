#!/usr/bin/env python

import unittest, os, shutil
from planet import config, splice

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

        for file in ['index.html', 'default.css', 'images/foaf.png']:
            path = os.path.join(workdir, file)
            self.assertTrue(os.path.exists(path))
            self.assertTrue(os.stat(path).st_size > 0)
