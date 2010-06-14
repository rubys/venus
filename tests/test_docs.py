#!/usr/bin/env python

import unittest, os, re
from xml.dom import minidom
from glob import glob
from htmlentitydefs import name2codepoint as n2cp

class DocsTest(unittest.TestCase):

    def test_well_formed(self):
        def substitute_entity(match):
            ent = match.group(1)
            try:
                  return "&#%d;" % n2cp[ent]
            except:
                  return "&%s;" % ent

        for doc in glob('docs/*'):
            if os.path.isdir(doc): continue
            if doc.endswith('.css') or doc.endswith('.js'): continue

            source = open(doc).read()
            source = re.sub('&(\w+);', substitute_entity, source)

            try:
                minidom.parseString(source)
            except:
                self.fail('Not well formed: ' + doc);
                break
        else:
            self.assertTrue(True);
