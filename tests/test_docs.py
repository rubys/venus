#!/usr/bin/env python
# coding=utf-8

import os
import re
import unittest
from glob import glob
from htmlentitydefs import name2codepoint as n2cp
from xml.dom import minidom


class DocsTest(unittest.TestCase):
    def test_well_formed(self):
        def substitute_entity(match):
            ent = match.group(1)
            try:
                return "&#%d;" % n2cp[ent]
            except:
                return "&%s;" % ent

        for doc in glob('docs/*'):
            if os.path.isdir(doc):
                continue
            if doc.endswith('.css') or doc.endswith('.js'):
                continue
            with open(doc) as fp:
                source = fp.read()
                source = re.sub('&(\w+);', substitute_entity, source)

            try:
                minidom.parseString(source)
            except:
                self.fail('Not well formed: ' + doc)

        else:
            self.assertTrue(True)
