#!/usr/bin/env python

import os.path
import unittest
import xml.dom.minidom
import datetime

from planet import config, logger
from planet.shell import dj


class DjangoFilterTests(unittest.TestCase):

    def test_django_filter(self):
        config.load('tests/data/filter/django/test.ini')
        results = dj.tmpl.template_info("<feed/>")
        self.assertEqual(results['name'], 'Django on Venus')

    def test_django_date_type(self):
        config.load('tests/data/filter/django/test.ini')
        results = dj.tmpl.template_info("<feed/>")
        self.assertEqual(type(results['date']), datetime.datetime)

    def test_django_entry_title(self):
        config.load('tests/data/filter/django/test.ini')
        feed = open('tests/data/filter/django/test.xml')
        input = feed.read()
        feed.close()
        results = dj.run(
            os.path.realpath('tests/data/filter/django/title.html.dj'), input)
        self.assertEqual(results,
                         u"\xa1Atom-Powered &lt;b&gt;Robots&lt;/b&gt; Run Amok!\n")

    def test_django_entry_title_autoescape_off(self):
        config.load('tests/data/filter/django/test.ini')
        config.parser.set('Planet', 'django_autoescape', 'off')
        feed = open('tests/data/filter/django/test.xml')
        input = feed.read()
        feed.close()
        results = dj.run(
            os.path.realpath('tests/data/filter/django/title.html.dj'), input)
        self.assertEqual(
            results,
            u"\xa1Atom-Powered <b>Robots</b> Run Amok!\n")

    def test_django_config_context(self):
        config.load('tests/data/filter/django/test.ini')
        feed = open('tests/data/filter/django/test.xml')
        input = feed.read()
        feed.close()
        results = dj.run(
            os.path.realpath('tests/data/filter/django/config.html.dj'), input)
        self.assertEqual(results, "Django on Venus\n")


try:
    from django.conf import settings
except ImportError:
    logger.warn("Django is not available => can't test django filters")
    for method in dir(DjangoFilterTests):
        if method.startswith('test_'):
            delattr(DjangoFilterTests, method)
