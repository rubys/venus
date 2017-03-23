Etiquette
---------

You would think that people who publish syndication feeds do it with
the intent to be syndicated. But the truth is that we live in a world
where `deep linking`_ can cause people to complain. Nothing is safe.
But that doesnt stop us from doing links.

These concerns tend to increase when you profit, either directly via
ads or indirectly via search engine rankings, from the content of
others.

While there are no hard and fast rules that apply here, heres are a
few things you can do to mitigate the concern:


+ Aggressively use robots.txt, meta tags, and the google/livejournal
  atom namespace to mark your pages as not to be indexed by search
  engines.

    :robots.txt_: `User-agent: * > Disallow:`

    :index.html: `\<meta name="robots" content="noindex,nofollow"/\>`_

    :atom.xml: `\<feed xmlns:indexing="urn:atom-extension:indexing" indexing:index="no"\>`_

               `\<access:restriction xmlns:access="http://www.bloglines.com/about/specs/fac-1.0" relationship="deny"/\>`_


+ Ensure that all `copyright`_ and `licensing`_ information is
  propagated to the combined feed(s) that you produce.
+ Add no advertising. Consider filtering out ads, lest you be accused
  of using someones content to help your friends profit.
+ Most importantly, if anyone does object to their content being
  included, quickly and without any complaint, remove them.


.. _robots.txt: http://www.robotstxt.org/
.. _<meta name="robots" content="noindex,nofollow"/>: http://www.robotstxt.org/wc/meta-user.html
.. _<feed xmlns:indexing="urn:atom-extension:indexing" indexing:index="no">: http://community.livejournal.com/lj_dev/696793.html
.. _<access:restriction xmlns:access="http://www.bloglines.com/about/specs/fac-1.0" relationship="deny"/>: http://www.bloglines.com/about/specs/fac-1.0


.. _copyright: http://nightly.feedparser.org/docs/reference-entry-source.html#reference.entry.source.rights
.. _licensing: http://nightly.feedparser.org/docs/reference-entry-license.html
.. _deep linking: http://en.wikipedia.org/wiki/Deep_linking


