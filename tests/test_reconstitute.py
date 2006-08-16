#!/usr/bin/env python

import unittest, os, sys, glob, new, re, StringIO, time
from planet import feedparser
from planet.reconstitute import reconstitute

testfiles = 'tests/data/reconstitute/%s.xml'

class ReconstituteTest(unittest.TestCase):
    desc_re = re.compile("Description:\s*(.*?)\s*Expect:\s*(.*)\s*-->")

    def eval(self, name):
        # read the test case
        try:
            testcase = open(testfiles % name)
            data = testcase.read()
            description, expect = self.desc_re.search(data).groups()
            testcase.close()
        except:
            raise RuntimeError, "can't parse %s" % name

        # parse and reconstitute to a string
        work = StringIO.StringIO()
        results = feedparser.parse(data)
        reconstitute(results, results.entries[0]).writexml(work)

        # verify the results
        results = feedparser.parse(work.getvalue().encode('utf-8'))
        self.assertFalse(results.bozo, 'xml is well formed')
        self.assertTrue(eval(expect, results.entries[0]), expect)

# build a test method for each test file
for testcase in glob.glob(testfiles % '*'):
    root = os.path.splitext(os.path.basename(testcase))[0]
    func = lambda self, name=root: self.eval(name)
    method = new.instancemethod(func, None, ReconstituteTest)
    setattr(ReconstituteTest, "test_" + root, method)
