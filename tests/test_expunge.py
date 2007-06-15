#!/usr/bin/env python
import unittest, os, glob, shutil, time
from planet.spider import filename
from planet import feedparser, config
from planet.expunge import expungeCache
from xml.dom import minidom
import planet

workdir = 'tests/work/expunge/cache'
sourcesdir = 'tests/work/expunge/cache/sources'
testentries = 'tests/data/expunge/test*.entry'
testfeeds = 'tests/data/expunge/test*.atom'
configfile = 'tests/data/expunge/config.ini'

class ExpungeTest(unittest.TestCase):
    def setUp(self):
        # silence errors
        self.original_logger = planet.logger
        planet.getLogger('CRITICAL',None)

        try:
            os.makedirs(workdir)
            os.makedirs(sourcesdir)
        except:
            self.tearDown()
            os.makedirs(workdir)
            os.makedirs(sourcesdir)
             
    def tearDown(self):
        shutil.rmtree(workdir)
        os.removedirs(os.path.split(workdir)[0])
        planet.logger = self.original_logger

    def test_expunge(self):
        config.load(configfile)

        # create test entries in cache with correct timestamp
        for entry in glob.glob(testentries):
            e=minidom.parse(entry)
            e.normalize()
            eid = e.getElementsByTagName('id')
            efile = filename(workdir, eid[0].childNodes[0].nodeValue)
            eupdated = e.getElementsByTagName('updated')[0].childNodes[0].nodeValue
            emtime = time.mktime(feedparser._parse_date_w3dtf(eupdated))
            if not eid or not eupdated: continue
            shutil.copyfile(entry, efile)
            os.utime(efile, (emtime, emtime))
  
        # create test feeds in cache
        sources = config.cache_sources_directory()
        for feed in glob.glob(testfeeds):
                f=minidom.parse(feed)
                f.normalize()
                fid = f.getElementsByTagName('id')
                if not fid: continue
                ffile = filename(sources, fid[0].childNodes[0].nodeValue)
                shutil.copyfile(feed, ffile)

        # verify that exactly nine entries + one source dir were produced
        files = glob.glob(workdir+"/*")
        self.assertEqual(10, len(files))

        # verify that exactly four feeds were produced in source dir
        files = glob.glob(sources+"/*")
        self.assertEqual(4, len(files))

        # expunge...
        expungeCache()

        # verify that five entries and one source dir are left
        files = glob.glob(workdir+"/*")
        self.assertEqual(6, len(files))

        # verify that the right five entries are left
        self.assertTrue(os.path.join(workdir,
            'bzr.mfd-consult.dk,2007,venus-expunge-test1,1') in files)
        self.assertTrue(os.path.join(workdir,
            'bzr.mfd-consult.dk,2007,venus-expunge-test2,1') in files)
        self.assertTrue(os.path.join(workdir,
            'bzr.mfd-consult.dk,2007,venus-expunge-test3,3') in files)
        self.assertTrue(os.path.join(workdir,
            'bzr.mfd-consult.dk,2007,venus-expunge-test4,2') in files)
        self.assertTrue(os.path.join(workdir,
            'bzr.mfd-consult.dk,2007,venus-expunge-test4,3') in files)
