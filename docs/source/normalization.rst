Normalization
-------------

Venus builds on, and extends, the `Universal Feed Parser`_ and
`html5lib`_ to convert all feeds into Atom 1.0, with well formed
XHTML, and encoded as UTF-8, meaning that you don't have to worry
about funky feeds, tag soup, or character encoding.


Encoding
~~~~~~~~

Input data in feeds may be encoded in a variety of formats, most
commonly ASCII, ISO-8859-1, WIN-1252, AND UTF-8. Additionally, many
feeds make use of the wide range of `character entity references`_
provided by HTML. Each is converted to UTF-8, an encoding which is a
proper superset of ASCII, supports the entire range of Unicode
characters, and is one of `only two`_ encodings required to be
supported by all conformant XML processors.

Encoding problems are one of the more common feed errors, and every
attempt is made to correct common errors, such as the inclusion of the
so-called `moronic`_ versions of smart-quotes. In rare cases where
individual characters can not be converted to valid UTF-8 or
into `characters allowed in XML 1.0 documents`_, such characters will
be replaced with the Unicode `Replacement character`_, with a title
that describes the original character whenever possible.

In order to support the widest range of inputs, use of Python 2.3 or
later, as well as the installation of the python `iconvcodec`, is
recommended.


HTML
~~~~

A number of different normalizations of HTML are performed. For
starters, the HTML is `sanitized`_, meaning that HTML tags and
attributes that could introduce javascript or other security risks are
removed.

Then, `relative links are resolved`_ within the HTML. This is also done
for links in other areas in the feed too.

Finally, unmatched tags are closed. This is done with a `knowledge of
the semantics of HTML`_. Additionally, a `large subset of MathML`_, as
well as a `tiny profile of SVG`_ is also supported.


Atom 1.0
~~~~~~~~

The Universal Feed Parser also `normalizes the content of feeds`_. This
involves a `large number of elements`_; the best place to start is to
look at `annotated examples`_. Among other things a wide variety
of `date formats`_ are converted into `RFC 3339`_ formatted dates.

If no `ids`_ are found in entries, attempts are made to synthesize one
using (in order):


+ `link`_
+ `title`_
+ `summary`_
+ `content`_


If no `updated`_ dates are found in an entry, the updated date from
the feed is used. If no updated date is found in either the feed or
the entry, the current time is substituted.


Overrides
~~~~~~~~~

All of the above describes what Venus does automatically, either
directly or through its dependencies. There are a number of errors
which can not be corrected automatically, and for these, there are
configuration parameters that can be used to help.


+ `ignore_in_feed` allows you to list any number of elements or
  attributes which are to be ignored in feeds. This is often handy in
  the case of feeds where the `author`, `id`, `updated` or `xml:lang`
  values can't be trusted.
+ `title_type`, `summary_type`, `content_type` allow you to override
  the `type`_ attributes on these elements.
+ `name_type` does something similar for `author names`_
+ `future_dates` allows you to specify how to deal with dates which
  are in the future.

    + `ignore_date` will cause the date to be ignored (and will therefore
      default to the time the entry was first seen) until the feed is
      updated and the time indicated is past, at which point the entry will
      be updated with the new date.
    + `ignore_entry` will cause the entire entry containing the future
      date to be ignored until the date is past.
    + Anything else (i.e.. the default) will leave the date as is, causing
      the entries that contain these dates sort to the top of the planet
      until the time passes.

+ `xml_base` will adjust the `xml:base` values in effect for each of
  the text constructs in the feed (things like `title`, `summary`, and
  `content`). Other elements in the feed (most notably, `link` are not
  affected by this value.

    + `feed_alternate` will replace the `xml:base` in effect with the
      value of the `alternate` `link` found either in the enclosed `source`
      or enclosing `feed` element.
    + `entry_alternate` will replace the `xml:base` in effect with the
      value of the `alternate` `link` found in this entry.
    + Any other value will be treated as a `URI reference`_. These values
      may be relative or absolute. If relative, the `xml:base` values in
      each text construct will each be adjusted separately using to the
      specified value.



.. _large subset of MathML: http://golem.ph.utexas.edu/~distler/blog/archives/000165.html#sanitizespec
.. _tiny profile of SVG: http://www.w3.org/TR/SVGMobile/
.. _large number of elements: http://www.feedparser.org/docs/reference.html
.. _type: http://www.feedparser.org/docs/reference-entry-title_detail.html#reference.entry.title_detail.type
.. _annotated examples: http://www.feedparser.org/docs/annotated-examples.html
.. _author names: http://www.feedparser.org/docs/reference-entry-author_detail.html#reference.entry.author_detail.name
.. _date formats: http://www.feedparser.org/docs/date-parsing.html
.. _relative links are resolved: http://www.feedparser.org/docs/resolving-relative-links.html
.. _characters allowed in XML 1.0 documents: http://www.w3.org/TR/xml/#charsets
.. _link: http://www.feedparser.org/docs/reference-entry-link.html
.. _normalizes the content of feeds: http://www.feedparser.org/docs/content-normalization.html
.. _title: http://www.feedparser.org/docs/reference-entry-title.html
.. _moronic: http://www.fourmilab.ch/webtools/demoroniser/
.. _sanitized: http://www.feedparser.org/docs/html-sanitization.html
.. _RFC 3339: http://www.ietf.org/rfc/rfc3339.txt
.. _content: http://www.feedparser.org/docs/reference-entry-content.html
.. _character entity references: http://www.w3.org/TR/html401/sgml/entities.html
.. _updated: http://www.feedparser.org/docs/reference-feed-updated.html
.. _Replacement character: http://www.fileformat.info/info/unicode/char/fffd/index.htm
.. _only two: http://www.w3.org/TR/2006/REC-xml-20060816/#charsets
.. _summary: http://www.feedparser.org/docs/reference-entry-summary.html
.. _knowledge of the semantics of HTML: http://code.google.com/p/html5lib/
.. _ids: http://www.feedparser.org/docs/reference-entry-id.html
.. _Universal Feed Parser: http://www.feedparser.org/
.. _URI reference: http://www.ietf.org/rfc/rfc3986.txt
.. _html5lib: https://github.com/html5lib/

