Filters and Plugins
-------------------

Filters and plugins are simple Unix pipes. Input comes in `stdin`,
parameters come from the config file, and output goes to `stdout`.
Anything written to `stderr` is logged as an ERROR message. If no
`stdout` is produced, the entry is not written to the cache or
processed further; in fact, if the entry had previously been written
to the cache, it will be removed.

There are two types of filters supported by Venus, input and template.

Input to an input filter is a aggressively `normalized`_ entry. For
example, if a feed is RSS 1.0 with 10 items, the filter will be called
ten times, each with a single Atom 1.0 entry, with all textConstructs
expressed as XHTML, and everything encoded as UTF-8.

Input to a template filter will be the output produced by the
template.

You will find a small set of example filters in the `filters`_
directory. The `coral cdn filter`_ will change links to images in the
entry itself. The filters in the `stripAd`_ subdirectory will strip
specific types of advertisements that you may find in feeds.

The `excerpt`_ filter adds metadata (in the form of a `planet:excerpt`
element) to the feed itself. You can see examples of how parameters
are passed to this program in either `excerpt-images`_ or `opml-top100.ini`_.
Alternately parameters may be passed URI style, for
example: `excerpt-images2`_.

The `xpath sifter`_ is a variation of the above, including or
excluding feeds based on the presence (or absence) of data specified
by `xpath`_ expressions. Again, parameters can be passed as `config
options`_ or `URI style`_.

The `regexp sifter`_ operates just like the xpath sifter, except it
uses `regular expressions`_ instead of XPath expressions.



Notes
~~~~~


+ Any filters listed in the `[planet]` section of your config.ini will
  be invoked on all feeds. Filters listed in individual `[feed]`
  sections will only be invoked on those feeds. Filters listed in
  `[template]` sections will be invoked on the output of that template.

+ Input filters are executed when a feed is fetched, and the results
  are placed into the cache. Changing a configuration file alone is not
  sufficient to change the contents of the cache typically that only
  occurs after a feed is modified.

+ Filters are simply invoked in the order they are listed in the
  configuration file (think unix pipes). Planet wide filters are
  executed before feed specific filters.

+ The file extension of the filter is significant. `.py` invokes
  python. `.xslt` involkes XSLT. `.sed` and `.tmpl` (a.k.a. htmltmp) are
  also options. Other languages, like perl or ruby or class/jar (java),
  aren't supported at the moment, but these would be easy to add.

+ If the filter name contains a redirection character ( `>`), then the
  output stream is `tee`_ d; one branch flows through the specified filter
  and the output is planced into the named file; the other unmodified
  branch continues onto the next filter, if any. One use case for this
  function is to use `xhtml2html`_ to produce both an XHTML and an HTML
  output stream from one source.

+ Templates written using htmltmpl or django currently only have
  access to a fixed set of fields, whereas XSLT and genshi templates
  have access to everything.

+ Plugins differ from filters in that while filters are forked,
  plugins are `imported`_. This means that plugins are limited to Python
  and are run in-process. Plugins therefore have direct access to planet
  internals like configuration and logging facitilies, as well as access
  to the bundled libraries like the `Universal Feed Parser`_
  and `html5lib`_ ; but it also means that functions like `os.abort()`
  can't be recovered from.


.. _coral cdn filter: ../filters/coral_cdn_filter.py
.. _URI style: ../tests/data/filter/xpath-sifter2.ini
.. _normalized: normalization.html
.. _xpath sifter: ../filters/xpath_sifter.py
.. _tee: http://en.wikipedia.org/wiki/Tee_(Unix)
.. _html5lib: http://code.google.com/p/html5lib/
.. _excerpt-images: ../tests/data/filter/excerpt-images.ini
.. _regexp sifter: ../filters/regexp_sifter.py
.. _xhtml2html: ../filters/xhtml2html.plugin
.. _stripAd: ../filters/stripAd/
.. _config options: ../tests/data/filter/xpath-sifter.ini
.. _filters: ../filters
.. _excerpt-images2: ../tests/data/filter/excerpt-images2.ini
.. _xpath: http://www.w3.org/TR/xpath20/
.. _opml-top100.ini: ../examples/opml-top100.ini
.. _regular expressions: http://docs.python.org/lib/re-syntax.html
.. _Universal Feed Parser: http://feedparser.org/docs/
.. _excerpt: ../filters/excerpt.py
.. _imported: http://docs.python.org/lib/module-imp.html


