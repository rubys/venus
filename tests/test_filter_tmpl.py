#!/usr/bin/env python

import unittest, os, sys, glob, new, re, StringIO, time
from planet.shell import tmpl

testfiles = 'tests/data/filter/tmpl/%s.xml'

class FilterTmplTest(unittest.TestCase):
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

        # map to template info
        results = tmpl.template_info(data)

        # verify the results
        if not self.simple_re.match(expect):
            self.assertTrue(eval(expect, results), expect)
        else:
            lhs, rhs = self.simple_re.match(expect).groups()
            self.assertEqual(eval(rhs), eval(lhs, results))

# build a test method for each test file
for testcase in glob.glob(testfiles % '*'):
    root = os.path.splitext(os.path.basename(testcase))[0]
    func = lambda self, name=root: self.eval(name)
    method = new.instancemethod(func, None, FilterTmplTest)
    setattr(FilterTmplTest, "test_" + root, method)
