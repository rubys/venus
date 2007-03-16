#!/usr/bin/env python

import unittest, os
from xml.dom import minidom
from glob import glob

class DocsTest(unittest.TestCase):

    def test_well_formed(self):
        for doc in glob('docs/*'):
            if os.path.isdir(doc): continue
            if doc.endswith('.css') or doc.endswith('.js'): continue

            try:
                minidom.parse(doc)
            except:
                self.fail('Not well formed: ' + doc);
                break
        else:
            self.assertTrue(True);
