#!/usr/bin/env python

import unittest
from planet import idindex, config, logger

class idIndexTest(unittest.TestCase):

    def tearDown(self):
        idindex.destroy()

    def test_index_spider(self):
        import test_spider
        config.load(test_spider.configfile)

        index = idindex.create()
        self.assertEqual(0, len(index))
        index.close()

        from planet.spider import spiderPlanet
        try:
            spiderPlanet()

            index = idindex.open()
            self.assertEqual(12, len(index))
            self.assertEqual('tag:planet.intertwingly.net,2006:testfeed1', index['planet.intertwingly.net,2006,testfeed1,1'])
            self.assertEqual('http://intertwingly.net/code/venus/tests/data/spider/testfeed3.rss', index['planet.intertwingly.net,2006,testfeed3,1'])
            index.close()
        finally:
            import os, shutil
            shutil.rmtree(test_spider.workdir)
            os.removedirs(os.path.split(test_spider.workdir)[0])

    def test_index_splice(self):
        import test_splice
        config.load(test_splice.configfile)
        index = idindex.create()

        self.assertEqual(12, len(index))
        self.assertEqual('tag:planet.intertwingly.net,2006:testfeed1', index['planet.intertwingly.net,2006,testfeed1,1'])
        self.assertEqual('http://intertwingly.net/code/venus/tests/data/spider/testfeed3.rss', index['planet.intertwingly.net,2006,testfeed3,1'])

        for key,value in index.items():
            if value.find('testfeed2')>0: index[key] = value[::-1]
        index.close()

        from planet.splice import splice
        doc = splice()

        self.assertEqual(8,len(doc.getElementsByTagName('entry')))
        self.assertEqual(4,len(doc.getElementsByTagName('planet:source')))
        self.assertEqual(12,len(doc.getElementsByTagName('planet:name')))

try:
    import libxml2
except ImportError:
    logger.warn("libxml2 is not available => can't test id index")
    for method in dir(idIndexTest):
        if method.startswith('test_'):  delattr(idIndexTest,method)
