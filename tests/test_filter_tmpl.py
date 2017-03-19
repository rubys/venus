#!/usr/bin/env python
# coding=utf-8

import glob
import new
import os
import re
import unittest

from planet import config
from planet.shell import tmpl

testfiles = 'tests/data/filter/tmpl/%s.%s'


class FilterTmplTest(unittest.TestCase):
    desc_feed_re = re.compile("Description:\s*(.*?)\s*Expect:\s*(.*)\s*-->")
    desc_config_re = re.compile(";\s*Description:\s*(.*?)\s*;\s*Expect:\s*(.*)")
    simple_re = re.compile("^(\S+) == (u?'[^']*'|\([0-9, ]+\))$")

    def eval_feed(self, name):
        # read the test case
        try:
            with open(testfiles % (name, 'xml')) as testcasefile:
                data = testcasefile.read()
            description, expect = self.desc_feed_re.search(data).groups()
        except:
            raise RuntimeError("can't parse %s" % name)

        # map to template info
        results = tmpl.template_info(data)

        # verify the results
        if not self.simple_re.match(expect):
            self.assertTrue(eval(expect, results), expect)
        else:
            lhs, rhs = self.simple_re.match(expect).groups()
            self.assertEqual(eval(rhs), eval(lhs, results))

    def eval_config(self, name):
        # read the test case
        try:
            with open(testfiles % (name, 'ini')) as testcasefile:
                data = testcasefile.read()
            description, expect = self.desc_config_re.search(data).groups()
        except:
            raise RuntimeError("can't parse %s" % name)

        # map to template info
        config.load(testfiles % (name, 'ini'))
        results = tmpl.template_info("<feed/>")

        # verify the results
        if not self.simple_re.match(expect):
            self.assertTrue(eval(expect, results), expect)
        else:
            lhs, rhs = self.simple_re.match(expect).groups()
            self.assertEqual(eval(rhs), eval(lhs, results))


# build a test method for each xml test file
for testcase in glob.glob(testfiles % ('*', 'xml')):
    root = os.path.splitext(os.path.basename(testcase))[0]
    func = lambda self, name=root: self.eval_feed(name)
    method = new.instancemethod(func, None, FilterTmplTest)
    setattr(FilterTmplTest, "test_" + root, method)

# build a test method for each ini test file
for testcase in glob.glob(testfiles % ('*', 'ini')):
    root = os.path.splitext(os.path.basename(testcase))[0]
    func = lambda self, name=root: self.eval_config(name)
    method = new.instancemethod(func, None, FilterTmplTest)
    setattr(FilterTmplTest, "test_" + root, method)
