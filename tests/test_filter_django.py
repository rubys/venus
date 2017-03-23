#!/usr/bin/env python
# coding=utf-8

import datetime
import os.path
import unittest

import pytest

from planet import config
from planet.shell import dj

try:
    from django.conf import settings

    django_available = True
except ImportError:
    django_available = False


@pytest.mark.skipif(not django_available, reason="Django is not available => can't test django filters")
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
        with open('tests/data/filter/django/test.xml') as feed:
            input_ = feed.read()
        results = dj.run(
            os.path.realpath('tests/data/filter/django/title.html.dj'), input_)
        self.assertEqual(results,
                         u"\xa1Atom-Powered &lt;b&gt;Robots&lt;/b&gt; Run Amok!\n")

    def test_django_entry_title_autoescape_off(self):
        config.load('tests/data/filter/django/test.ini')
        config.parser.set('Planet', 'django_autoescape', 'off')
        with open('tests/data/filter/django/test.xml') as feed:
            input_ = feed.read()
        results = dj.run(
            os.path.realpath('tests/data/filter/django/title.html.dj'), input_)
        self.assertEqual(results, u"\xa1Atom-Powered <b>Robots</b> Run Amok!\n")

    def test_django_config_context(self):
        config.load('tests/data/filter/django/test.ini')
        with open('tests/data/filter/django/test.xml') as feed:
            input_ = feed.read()
        results = dj.run(
            os.path.realpath('tests/data/filter/django/config.html.dj'), input_)
        self.assertEqual(results, "Django on Venus\n")
