#!/usr/bin/env python

import unittest, os, sys, glob, new, re, StringIO, time
from planet import feedparser
from planet.reconstitute import reconstitute
from planet.scrub import scrub

testfiles = 'tests/data/reconstitute/%s.xml'

class ReconstituteTest(unittest.TestCase):
    desc_re = re.compile("Description:\s*(.*?)\s*Expect:\s*(.*)\s*-->")
    simple_re = re.compile("^(\S+) == (u?'[^']*'|\([0-9, ]+\))$")

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
        scrub(testfiles%name, results)
        reconstitute(results, results.entries[0]).writexml(work)

        # verify the results
        results = feedparser.parse(work.getvalue().encode('utf-8'))
        self.assertFalse(results.bozo, 'xml is well formed')
        if not self.simple_re.match(expect):
            self.assertTrue(eval(expect, results.entries[0]), expect)
        else:
            lhs, rhs = self.simple_re.match(expect).groups()
            self.assertEqual(eval(rhs), eval(lhs, results.entries[0]))

# build a test method for each test file
for testcase in glob.glob(testfiles % '*'):
    root = os.path.splitext(os.path.basename(testcase))[0]
    func = lambda self, name=root: self.eval(name)
    method = new.instancemethod(func, None, ReconstituteTest)
    setattr(ReconstituteTest, "test_" + root, method)
