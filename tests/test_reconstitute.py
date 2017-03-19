#!/usr/bin/env python
# coding=utf-8

from StringIO import StringIO
import re

from planet import feedparser
from planet.reconstitute import reconstitute
from planet.scrub import scrub


desc_re = re.compile("Description:\s*(.*?)\s*Expect:\s*(.*)\s*-->")
simple_re = re.compile("^(\S+) == (u?'[^']*'|\([0-9, ]+\))$")


def test_reconstitute(xml_reconstitute):
    # read the test case
    try:
        with open(xml_reconstitute) as testcasefile:
            data = testcasefile.read()
            description, expect = desc_re.search(data).groups()
    except:
        raise RuntimeError("can't parse %s" % xml_reconstitute)

    # parse and reconstitute to a string
    work = StringIO()
    results = feedparser.parse(data)
    scrub(xml_reconstitute, results)
    reconstitute(results, results.entries[0]).writexml(work)

    # verify the results
    results = feedparser.parse(work.getvalue().encode('utf-8'))

    if 'illegal' not in xml_reconstitute:
        assert not results.bozo, 'xml is well formed'

    if not simple_re.match(expect):
        assert eval(expect, results.entries[0]), expect
    else:
        lhs, rhs = simple_re.match(expect).groups()
        assert eval(rhs) == eval(lhs, results.entries[0])
