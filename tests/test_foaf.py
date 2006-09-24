#!/usr/bin/env python

import unittest, os, shutil
from planet.foaf import foaf2config
from ConfigParser import ConfigParser
from planet import config, logger

workdir = 'tests/work/config/cache'

blogroll = 'http://journal.dajobe.org/journal/2003/07/semblogs/bloggers.rdf'
testfeed = "http://dannyayers.com/feed/rdf"
test_foaf_document = '''
<rdf:RDF
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:foaf="http://xmlns.com/foaf/0.1/"
  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
  xmlns:rss="http://purl.org/rss/1.0/"
  xmlns:dc="http://purl.org/dc/elements/1.1/">

<foaf:Agent rdf:nodeID="id2245354"> 
<foaf:name>Danny Ayers</foaf:name> 
<rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Person"/> 
<foaf:weblog> 
<foaf:Document rdf:about="http://dannyayers.com/"> 
<dc:title>Raw Blog by Danny Ayers</dc:title> 
<rdfs:seeAlso> 
<rss:channel rdf:about="http://dannyayers.com/feed/rdf"> 
<foaf:maker rdf:nodeID="id2245354"/> 
<foaf:topic rdf:resource="http://www.w3.org/2001/sw/"/> 
<foaf:topic rdf:resource="http://www.w3.org/RDF/"/> 
</rss:channel> 
</rdfs:seeAlso> 
</foaf:Document> 
</foaf:weblog> 
<foaf:interest rdf:resource="http://www.w3.org/2001/sw/"/> 
<foaf:interest rdf:resource="http://www.w3.org/RDF/"/> 
</foaf:Agent> 

</rdf:RDF> 
'''.strip()

class FoafTest(unittest.TestCase):
    """
    Test the foaf2config function
    """

    def setUp(self):
        self.config = ConfigParser()
        self.config.add_section(blogroll)

    def tearDown(self):
        if os.path.exists(workdir):
            shutil.rmtree(workdir)
            os.removedirs(os.path.split(workdir)[0])

    #
    # Tests
    #

    def test_foaf_document(self):
        foaf2config(test_foaf_document, self.config)
        self.assertEqual('Danny Ayers', self.config.get(testfeed, 'name'))

    def test_no_foaf_name(self):
        test = test_foaf_document.replace('foaf:name','foaf:title')
        foaf2config(test, self.config)
        self.assertEqual('Raw Blog by Danny Ayers',
           self.config.get(testfeed, 'name'))

    def test_no_weblog(self):
        test = test_foaf_document.replace('rdfs:seeAlso','rdfs:seealso')
        foaf2config(test, self.config)
        self.assertFalse(self.config.has_section(testfeed))

    def test_invalid_xml_before(self):
        test = '\n<?xml version="1.0" encoding="UTF-8"?>' + test_foaf_document
        foaf2config(test, self.config)
        self.assertFalse(self.config.has_section(testfeed))

    def test_invalid_xml_after(self):
        test = test_foaf_document.strip()[:-1]
        foaf2config(test, self.config)
        self.assertEqual('Danny Ayers', self.config.get(testfeed, 'name'))

    def test_online_accounts(self):
        config.load('tests/data/config/foaf.ini')
        feeds = config.subscriptions()
        feeds.sort()
        self.assertEqual(['http://api.flickr.com/services/feeds/' +
            'photos_public.gne?id=77366516@N00',
            'http://del.icio.us/rss/eliast',
            'http://torrez.us/feed/rdf'], feeds)

    def test_multiple_subscriptions(self):
        config.load('tests/data/config/foaf-multiple.ini')
        self.assertEqual(2,len(config.reading_lists()))
        feeds = config.subscriptions()
        feeds.sort()
        self.assertEqual(5,len(feeds))
        self.assertEqual(['http://api.flickr.com/services/feeds/' +
            'photos_public.gne?id=77366516@N00',
            'http://api.flickr.com/services/feeds/' +
            'photos_public.gne?id=SOMEID',
            'http://del.icio.us/rss/SOMEID',
            'http://del.icio.us/rss/eliast',
            'http://torrez.us/feed/rdf'], feeds)

    def test_recursive(self):
        config.load('tests/data/config/foaf-deep.ini')
        feeds = config.subscriptions()
        feeds.sort()
        self.assertEqual(['http://api.flickr.com/services/feeds/photos_public.gne?id=77366516@N00',
        'http://del.icio.us/rss/eliast', 'http://del.icio.us/rss/leef',
        'http://del.icio.us/rss/rubys', 'http://intertwingly.net/blog/atom.xml',
        'http://thefigtrees.net/lee/life/atom.xml',
        'http://torrez.us/feed/rdf'], feeds)

# these tests only make sense if libRDF is installed
try:
    import RDF
except:
    logger.warn("Redland RDF is not available => can't test FOAF reading lists")
    for key in FoafTest.__dict__.keys():
        if key.startswith('test_'): delattr(FoafTest, key)

if __name__ == '__main__':
    unittest.main()
