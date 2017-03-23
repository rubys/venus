Templates
---------

Template names take the form *name* `.` *ext* `.` *type*, where *name*
`.` *ext* identifies the name of the output file to be created in the
`output_directory`, and *type* indicates which language processor to
use for the template.

Like with `filters`_, templates may be written in a variety of
languages and are based on the standard Unix pipe convention of
producing `stdout` from `stdin`, but in practice two languages are
used more than others:


htmltmpl
~~~~~~~~

Many find `htmltmpl`_ easier to get started with as you can take a
simple example of your output file, sprinkle in a few `<TMPL_VAR>` s
and `<TMPL_LOOP>` s and you are done. Eventually, however, you may find
that your template involves `<TMPL_IF>` blocks inside of attribute
values, and you may find the result difficult to read and create
correctly.

It is also important to note that htmltmpl based templates do not have
access to the full set of information available in the feed, just the
following (rather substantial) subset:

+------------------+------------+---------------------------------+
| VAR              | type       |  source                         |
+==================+============+=================================+
| author           | String     | `feed.author`_                  |
+------------------+------------+---------------------------------+
|author_name       | String     | `feed.author_detail.name`_      |
+------------------+------------+---------------------------------+
|generator         | String     | `feed.generator`_               |
+------------------+------------+---------------------------------+
| id               | String     | `feed.id`_                      |
+------------------+------------+---------------------------------+
| icon             | String     | `feed.icon`_                    |
+------------------+------------+---------------------------------+
| last_updated_822 | Rfc822     | `feed.updated_parsed`_          |
+------------------+------------+---------------------------------+
| last_updated_iso | Rfc3399    | `feed.updated_parsed`_          |
+------------------+------------+---------------------------------+
| last_updated     | PlanetDate | `feed.updated_parsed`_          |
+------------------+------------+---------------------------------+
| link             | String     | `feed.link`_                    |
+------------------+------------+---------------------------------+
| logo             | String     | `feed.logo`_                    |
+------------------+------------+---------------------------------+
| rights           | String     | `feed.rights_detail.value`_     |
+------------------+------------+---------------------------------+
| subtitle         | String     | `feed.subtitle_detail.value`_   |
+------------------+------------+---------------------------------+
| title            | String     | `feed.title_detail.value`_      |
+------------------+------------+---------------------------------+
| title_plain      | Plain      | `feed.title_detail.value`_      |
+------------------+------------+---------------------------------+
| url              | String     | `feed.links[rel='self'].href`_  |
|                  |            | `feed.headers['location']`_     |
+------------------+------------+---------------------------------+

Note: when multiple sources are listed, the last one wins

In addition to these variables, Planet Venus makes available two
arrays, `Channels` and `Items`, with one entry per subscription and
per output entry respectively. The data values within the `Channels`
array exactly match the above list. The data values within the `Items`
array are as follows:


+------------------+------------+-------------------------------------------+
| VAR              | type       | source                                    |
+==================+============+===========================================+
| author           | String     | `entries[i].author`_                      |
+------------------+------------+-------------------------------------------+
| author_email     | String     | `entries[i].author_detail.email`_         |
+------------------+------------+-------------------------------------------+
| author_name      | String     | `entries[i].author_detail.name`_          |
+------------------+------------+-------------------------------------------+
| author_uri       | String     | `entries[i].author_detail.href`_          |
+------------------+------------+-------------------------------------------+
| content_language | String     | `entries[i].content[0].language`_         |
+------------------+------------+-------------------------------------------+
| content          | String     | `entries[i].summary_detail.value`_        |
+                  +            +-------------------------------------------+
|                  |            | `entries[i].content[0].value`_            |
+------------------+------------+-------------------------------------------+
| date             | PlanetDate | `entries[i].published_parsed`_            |
+                  +            +-------------------------------------------+
|                  |            | `entries[i].updated_parsed`_              |
+------------------+------------+-------------------------------------------+
| date_822         | Rfc822     | `entries[i].published_parsed`_            |
+                  +            +-------------------------------------------+
|                  |            | `entries[i].updated_parsed`_              |
+------------------+------------+-------------------------------------------+
| date_iso         | Rfc3399    | `entries[i].published_parsed`_            |
+                  +            +-------------------------------------------+
|                  |            | `entries[i].updated_parsed`_              |
+------------------+------------+-------------------------------------------+
| enclosure_href   | String     | `entries[i].enclosures[0].href`_          |
+------------------+------------+-------------------------------------------+
| enclosure_length | String     | `entries[i].enclosures[0].length`_        |
+------------------+------------+-------------------------------------------+
| enclosure_type   | String     | `entries[i].enclosures[0].type`_          |
+------------------+------------+-------------------------------------------+
| guid_isPermaLink | String     | `entries[i].isPermaLink`_                 |
+------------------+------------+-------------------------------------------+
| id               | String     | `entries[i].id`_                          |
+------------------+------------+-------------------------------------------+
| link             | String     | `entries[i].links[rel='alternate'].href`_ |
+------------------+------------+-------------------------------------------+
| new_channel      | String     | `entries[i].id`_                          |
+------------------+------------+-------------------------------------------+
| new_date         | NewDate    | `entries[i].published_parsed`_            |
+                  +            +-------------------------------------------+
|                  |            | `entries[i].updated_parsed`_              |
+------------------+------------+-------------------------------------------+
| rights           | String     | `entries[i].rights_detail.value`_         |
+------------------+------------+-------------------------------------------+
| title_language   | String     | `entries[i].title_detail.language`_       |
+------------------+------------+-------------------------------------------+
| title_plain      | Plain      | `entries[i].title_detail.value`_          |
+------------------+------------+-------------------------------------------+
| title            | String     | `entries[i].title_detail.value`_          |
+------------------+------------+-------------------------------------------+
| summary_language | String     | `entries[i].summary_detail.language`_     |
+------------------+------------+-------------------------------------------+
| updated          | PlanetDate | `entries[i].updated_parsed`_              |
+------------------+------------+-------------------------------------------+
| updated_822      | Rfc822     | `entries[i].updated_parsed`_              |
+------------------+------------+-------------------------------------------+
| updated_iso      | Rfc3399    | `entries[i].updated_parsed`_              |
+------------------+------------+-------------------------------------------+
| published        | PlanetDate | `entries[i].published_parsed`_            |
+------------------+------------+-------------------------------------------+
| published_822    | Rfc822     | `entries[i].published_parsed`_            |
+------------------+------------+-------------------------------------------+
| published_iso    | Rfc3399    | `entries[i].published_parsed`_            |
+------------------+------------+-------------------------------------------+


Note: variables above which start with `new_` are only set if their
values differ from the previous Item.



django
~~~~~~

If you have the `Django`_ framework installed, `Django templates`_ are
automatically available to Venus projects. You will have to save them
with a `.html.dj` extension in your themes. The variable set is the
same as the one from htmltmpl, above. In the Django template context
you'll have access to `Channels` and `Items` and you'll be able to
iterate through them.

You also have access to the `Config` dictionary, which contains the
Venus configuration variables from your `.ini` file.

If you lose your way and want to introspect all the variable in the
context, there's the useful `{% debug %}` template tag.

In the `themes/django/` you'll find a sample Venus theme that uses the
Django templates that might be a starting point for your own custom
themes.

All the standard Django template tags and filter are supposed to work,
with the notable exception of the `date` filter on the updated and
published dates of an item (it works on the main `{{ date }}`
variable).

Please note that Django, and therefore Venus' Django support, requires
at least Python 2.3.

The `django_autoescape`_ config option may be used to globally set the
default value for `auto-escaping`_.



xslt
~~~~

`XSLT`_ is a paradox: it actually makes some simple things easier to
do than htmltmpl, and certainly can make more difficult things
possible; but it is fair to say that many find XSLT less approachable
than htmltmpl.

But in any case, the XSLT support is easier to document as the input
is a `highly normalized`_ feed, with a few extension elements.


+ `atom:feed` will have the following child elements:

    + A `planet:source` element per subscription, with the same child
      elements as `atom:source`_, as well as an additional child element
      in the planet namespace for each `configuration parameter`_ that
      applies to this subscription.
    + `planet:format`_ indicating the format and version of the source
      feed.
    + `planet:bozo`_ which is either `true` or `false`.

+ `atom:updated` and `atom:published` will have a `planet:format`
  attribute containing the referenced date formatted according to the
  `[planet] date_format` specified in the configuration




genshi
~~~~~~

Genshi approaches the power of XSLT, but with a syntax that many
Python programmers find more natural, succinct and expressive. Genshi
templates have access to the full range of `feedparser`_ values, with
the following additions:


+ In addition to a `feed` element which describes the feed for your
  planet, there is also a `feeds` element which contains the description
  for each subscription.
+ All `feed`, `feeds`, and `source` elements have a child `config`
  element which contains the config.ini entries associated with that
  feed.
+ All text construct detail elements ( `subtitle`, `rights`, `title`,
  `summary`, `content`) also contain a `stream` element which contains
  the value as a Genshi stream.
+ Each of the `entries` has a `new_date` and `new_feed` value which
  indicates if this entry's date or feed differs from the preceeding
  entry.

.. _atom:source: http://www.atomenabled.org/developers/syndication/atom-format-spec.php#element.source
.. _planet:format: http://www.feedparser.org/docs/reference-version.html
.. _planet:bozo: http://www.feedparser.org/docs/reference-bozo.html

.. _entries[i].author_detail.email: https://pythonhosted.org/feedparser/reference-entry-author_detail.html#reference.entry.author_detail.email
.. _entries[i].author_detail.href: https://pythonhosted.org/feedparser/reference-entry-author_detail.html#reference.entry.author_detail.href
.. _entries[i].author_detail.name: https://pythonhosted.org/feedparser/reference-entry-author_detail.html#reference.entry.author_detail.name
.. _auto-escaping: http://docs.djangoproject.com/en/dev/ref/templates/builtins/#autoescape
.. _configuration parameter: config.html#subscription
.. _entries[i].content[0].language: https://pythonhosted.org/feedparser/reference-entry-content.html#entries-i-content-j-language
.. _entries[i].content[0].value: https://pythonhosted.org/feedparser/reference-entry-content.html#entries-i-content-j-value
.. _Django templates: http://www.djangoproject.com/documentation/templates/
.. _Django: http://www.djangoproject.com/
.. _django_autoescape: config.html#django_autoescape
.. _entries[i].enclosures[0].href: https://pythonhosted.org/feedparser/reference-entry-enclosures.html#reference.entry.enclosures.href
.. _entries[i].enclosures[0].length: https://pythonhosted.org/feedparser/reference-entry-enclosures.html#reference.entry.enclosures.length
.. _entries[i].enclosures[0].type: https://pythonhosted.org/feedparser/reference-entry-enclosures.html#reference.entry.enclosures.type
.. _entries[i].author: https://pythonhosted.org/feedparser/reference-entry-author.html
.. _feed.author: https://pythonhosted.org/feedparser/reference-feed-author.html
.. _feed.author_detail.name: https://pythonhosted.org/feedparser/reference-feed-author_detail.html#reference.feed.author_detail.name
.. _feed.generator: https://pythonhosted.org/feedparser/reference-feed-generator.html
.. _feed.id: https://pythonhosted.org/feedparser/reference-feed-id.html
.. _feed.link: https://pythonhosted.org/feedparser/reference-feed-link.html
.. _feed.links[rel='self'].href: https://pythonhosted.org/feedparser/reference-feed-links.html#reference.feed.links.href
.. _feed.logo: https://pythonhosted.org/feedparser/reference-feed-logo.html
.. _feed.rights_detail.value: https://pythonhosted.org/feedparser/reference-feed-rights_detail.html#reference.feed.rights_detail.value
.. _feed.subtitle_detail.value: https://pythonhosted.org/feedparser/reference-feed-subtitle_detail.html#reference.feed.subtitle_detail.value
.. _feed.title_detail.value: https://pythonhosted.org/feedparser/reference-feed-title_detail.html#reference.feed.title_detail.value
.. _feed.updated_parsed: https://pythonhosted.org/feedparser/reference-feed-icon.html
.. _feedparser: https://pythonhosted.org/feedparser/reference.html
.. _filters: filters.html
.. _feed.headers['location']: https://pythonhosted.org/feedparser/reference-headers.html
.. _highly normalized: normalization.html
.. _htmltmpl: http://htmltmpl.sourceforge.net/
.. _entries[i].id: https://pythonhosted.org/feedparser/reference-entry-id.html
.. _entries[i].isPermaLink: http://blogs.law.harvard.edu/tech/rss#ltguidgtSubelementOfLtitemgt
.. _entries[i].links[rel='alternate'].href: https://pythonhosted.org/feedparser/reference-entry-links.html#reference.entry.links.href
.. _entries[i].published_parsed: https://pythonhosted.org/feedparser/reference-entry-published_parsed.html
.. _entries[i].rights_detail.value: https://pythonhosted.org/feedparser/reference-entry-rights_detail.html#reference.entry.rights_detail.value
.. _entries[i].summary_detail.language: https://pythonhosted.org/feedparser/reference-entry-summary_detail.html#reference.entry.summary_detail.language
.. _entries[i].summary_detail.value: https://pythonhosted.org/feedparser/reference-entry-summary_detail.html#reference.entry.summary_detail.value
.. _entries[i].title_detail.language: https://pythonhosted.org/feedparser/reference-entry-title_detail.html#reference.entry.title_detail.language
.. _entries[i].title_detail.value: https://pythonhosted.org/feedparser/reference-entry-title_detail.html#reference.entry.title_detail.value
.. _entries[i].updated_parsed: https://pythonhosted.org/feedparser/reference-entry-updated_parsed.html
.. _XSLT: http://www.w3.org/TR/xslt
.. _feed.icon: https://pythonhosted.org/feedparser/reference-feed-icon.html

