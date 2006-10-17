#!/usr/bin/env python
"""A filter to guess languages.

This filter guesses whether an Atom entry is written
in English or French. It should be trivial to chose between
two other languages, easy to extend to more than two languages
and useful to pass these languages as Venus configuration
parameters.

(See the REAME file for more details).

Requires Python 2.1, recommends 2.4.
"""
__authors__ = [ "Eric van der Vlist <vdv@dyomedea.com>"]
__license__ = "Python"

import amara
from sys import stdin, stdout
from trigram import Trigram
from xml.dom import XML_NAMESPACE as XML_NS
import cPickle

ATOM_NSS = {
    u'atom': u'http://www.w3.org/2005/Atom',
    u'xml': XML_NS
}

langs = {}

def tri(lang):
    if not langs.has_key(lang):
	f = open('filters/guess-language/%s.data' % lang, 'r')
	t = cPickle.load(f)
	f.close()
	langs[lang] = t
    return langs[lang]
    

def guess_language(entry):
    text = u'';
    for child in entry.xml_xpath(u'atom:title|atom:summary|atom:content'):
	text = text + u' '+ child.__unicode__()
    t = Trigram()
    t.parseString(text)
    if tri('fr') - t > tri('en') - t:
	lang=u'en'
    else:
	lang=u'fr'
    entry.xml_set_attribute((u'xml:lang', XML_NS), lang)

def main():
    feed = amara.parse(stdin, prefixes=ATOM_NSS)
    for entry in feed.xml_xpath(u'//atom:entry[not(@xml:lang)]'):
	guess_language(entry)
    feed.xml(stdout)

if __name__ == '__main__':
    main()
