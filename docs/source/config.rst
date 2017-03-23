.. role:: strike
    :class: strike

Configuration
-------------

Configuration files are in `ConfigParser`_ format which basically
means the same format as INI files, i.e., they consist of a series of
`[sections]`, in square brackets, with each section containing a list
of `name:value` pairs (or `name=value` pairs, if you prefer).

You are welcome to place your entire configuration into one file.
Alternately, you may factor out the templating into a "theme", and the
list of subscriptions into one or more "reading lists".


`[planet]`
~~~~~~~~~~

This is the only required section, which is a bit odd as none of the
parameters listed below are required. Even so, you really do want to
provide many of these, especially ones that identify your planet and
either (or both) of `template_files` and `theme`.

Below is a complete list of predefined planet configuration
parameters, including :strike:`ones not (yet) implemented by Venus` and ones
that are either new or implemented differently by Venus (marked with a `*` ).

:name: Your planet's name
:link: Link to the main page
:owner_name: Your name
:owner_email: Your e-mail address


:cache_directory: Where cached feeds are stored
:output_dir: Directory to place output files


:output_theme *: Directory containing a `config.ini` file which is
  merged with this one. This is typically used to specify templating and
  bill of material information.

:template_files: Space-separated list of output template files
:template_directories *:  Space-separated list of directories in which
  `template_files` can be found
:bill_of_materials *: Space-separated list of files to be copied as is
  directly from the `template_directories` to the `output_dir`
:filter: Regular expression that must be found in the textual portion
  of the entry
:exclude: Regular expression that must **not** be found in the textual
  portion of the entry
:filters *: Space-separated list of `filters`_ to apply to each entry
:filter_directories *: Space-separated list of directories in which
  `filters` can be found


:items_per_page: How many items to put on each page. Whereas Planet
  2.0 allows this to be overridden on a per template basis, Venus
  currently takes the maximum value for this across all templates.
:days_per_page: How many complete days of posts to put on each page
  This is the absolute, hard limit (over the item limit)
:date_format: `strftime`_ format for the default 'date' template
  variable
:new_date_format: `strftime`_ format for the 'new_date' template
  variable only applies to htmltmpl templates
:encoding: Output encoding for the file, Python 2.3+ users can use
  the special "xml" value to output ASCII with XML character references
:locale: Locale to use for (e.g.) strings in dates, default is taken
  from your system
:activity_threshold: If non-zero, all feeds which have not been
  updated in the indicated number of days will be marked as inactive


:log_level: One of `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL`
:log_format *: `format string`_ to use for logging output. Note: this
  configuration value is processed `raw`_
:feed_timeout: Number of seconds to wait for any given feed
:new_feed_items: Maximum number of items to include in the output from
  any one feed
:spider_threads *: The number of threads to use when spidering. When
  set to 0, the default, no threads are used and spidering follows the
  traditional algorithm.
:http_cache_directory *: If `spider_threads` is specified, you can
  also specify a directory to be used for an additional HTTP cache to
  front end the Venus cache. If specified as a relative path, it is
  evaluated relative to the `cache_directory`.
:cache_keep_entries *: Used by `expunge` to determine how many entries
  should be kept for each source when expunging old entries from the
  cache directory. This may be overriden on a per subscription feed
  basis.
:pubsubhubbub_hub *: URL to a PubSubHubbub hub, for example
  `http://pubsubhubbub.appspot.com`_. Used by `publish` to ping the hub
  when feeds are published, speeding delivery of updates to subscribers.
  See the `PubSubHubbub home page`_ for more information.
:pubsubhubbub_feeds *: List of feeds to publish. Defaults to `atom.xml
  rss10.xml rss20.xml`.
:django_autoescape *: Control `autoescaping`_ behavior of django
  templates. Defaults to `on`.


Additional options can be found in `normalization level overrides`_ .



`[DEFAULT]`
~~~~~~~~~~~

Values placed in this section are used as default values for all
sections. While it is true that few values make sense in all sections;
in most cases unused parameters cause few problems.



`[` *subscription* `]`
~~~~~~~~~~~~~~~~~~~~~~

All sections other than `planet`, `DEFAULT`, or are named in
`[planet]`'s `filters` or `templatefiles` parameters are treated as
subscriptions and typically take the form of a URI .

Parameters placed in this section are passed to templates. While you
are free to include as few or as many parameters as you like, most of
the predefined themes presume that at least `name` is defined.

The `content_type` parameter can be defined to indicate that this
subscription is a *reading list*, i.e., is an external list of
subscriptions. At the moment, three formats of reading lists are
supported: `opml`, `foaf`, `csv`, and `config`. In the future, support
for formats like `xoxo` could be added.

`Normalization overrides`_ can also be defined here.



`[` *template* `]`
~~~~~~~~~~~~~~~~~~

Sections which are listed in `[planet] template_files` are processed
as `templates`_. With Planet 2.0, it is possible to override
parameters like `items_per_page` on a per template basis, but at the
current time Planet Venus doesn't implement this.

`Filters`_ can be defined on a per-template basis, and will be used to
post-process the output of the template.



`[` *filter* `]`
~~~~~~~~~~~~~~~~

Sections which are listed in `[planet] filters` are processed as
`filters`_.

Parameters which are listed in this section are passed to the filter
in a language specific manner. Given the way defaults work, filters
should be prepared to ignore parameters that they didn't expect.

.. _filters: filters.html
.. _http://pubsubhubbub.appspot.com: http://pubsubhubbub.appspot.com
.. _Normalization overrides: normalization.html#overrides
.. _strftime: http://docs.python.org/lib/module-time.html#l2h-2816
.. _autoescaping: http://docs.djangoproject.com/en/dev/ref/templates/builtins/#autoescape
.. _templates: templates.html
.. _format string: http://docs.python.org/lib/node422.html
.. _PubSubHubbub home page: http://code.google.com/p/pubsubhubbub/
.. _raw: http://docs.python.org/lib/ConfigParser-objects.html
.. _ConfigParser: http://docs.python.org/lib/module-ConfigParser.html
.. _normalization level overrides: normalization.html#overrides



