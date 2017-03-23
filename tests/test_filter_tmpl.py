#!/usr/bin/env python
# coding=utf-8

import re

from planet import config
from planet.shell import tmpl

desc_feed_re = re.compile("Description:\s*(.*?)\s*Expect:\s*(.*)\s*-->")
desc_config_re = re.compile(";\s*Description:\s*(.*?)\s*;\s*Expect:\s*(.*)")
simple_re = re.compile("^(\S+) == (u?'[^']*'|\([0-9, ]+\))$")


def test_feed(xml_filter_template):
    # read the test case
    try:
        with open(xml_filter_template) as testcasefile:
            data = testcasefile.read()
        description, expect = desc_feed_re.search(data).groups()
    except:
        raise RuntimeError("can't parse %s" % xml_filter_template)

    # map to template info
    results = tmpl.template_info(data)

    # verify the results
    if not simple_re.match(expect):
        assert eval(expect, results), expect
    else:
        lhs, rhs = simple_re.match(expect).groups()
        assert eval(rhs) == eval(lhs, results)


def test_config(ini_filter_template):
    # read the test case
    try:
        with open(ini_filter_template) as testcasefile:
            data = testcasefile.read()
        description, expect = desc_config_re.search(data).groups()
    except:
        raise RuntimeError("can't parse %s" % ini_filter_template)

    # map to template info
    config.load(ini_filter_template)
    results = tmpl.template_info("<feed/>")

    # verify the results
    if not simple_re.match(expect):
        assert eval(expect, results), expect
    else:
        lhs, rhs = simple_re.match(expect).groups()
        assert eval(rhs) == eval(lhs, results)

