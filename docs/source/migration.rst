Migration from Planet 2.0
-------------------------

The intent is that existing Planet 2.0 users should be able to reuse
their existing `config.ini` and `.tmpl` files, but the reality is that
users will need to be aware of the following:


+ You will need to start over with a new cache directory as the format
  of the cache has changed dramatically.
+ Existing `.tmpl` and `.ini` files should work, though some
  `configuration`_ options (e.g., `days_per_page`) have not yet been
  implemented
+ No testing has been done on Python 2.1, and it is presumed not to
  work.
+ To take advantage of all features, you should install the optional
  XML and RDF libraries described on the `Installation`_ page.


Common changes to config.ini include:


+ Filename changes:

::

    
    examples/fancy/index.html.tmpl => themes/classic_fancy/index.html.tmpl
    examples/atom.xml.tmpl         => themes/common/atom.xml.xslt
    examples/rss20.xml.tmpl        => themes/common/rss20.xml.tmpl
    examples/rss10.xml.tmpl        => themes/common/rss10.xml.tmpl
    examples/opml.xml.tmpl         => themes/common/opml.xml.xslt
    examples/foafroll.xml.tmpl     => themes/common/foafroll.xml.xslt



.. _Installation: installation.html
.. _configuration: config.html


