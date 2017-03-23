Administration interface
------------------------

Venus comes with a basic administration interface, allowing you to
manually run planet, do a refresh from cache, expunge the cache or
blacklist individual entries from the planet.



Using the administration interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The administration interface allows you to manage the everyday tasks
related to your venus installation.


+ Running planet . By clicking the "Run planet" button, you can do a
  full run of the planet script, rechecking all the feeds and recreating
  the generated files. This corresponds to running `python planet.py
  config.ini` with no arguments. Note that, depending on the numer of
  feeds, this operation may take some time.
+ Refreshing planet . By clicking the "Refresh planet" button, you can
  do an "offline" run of the planet script, without rechecking all the
  feeds but still recreating the generated files. This corresponds to
  running `python planet.py -o config.ini`.
+ Expunging the planet cache . By clicking the "Expunge cache" button,
  you can clean the cache from outdated entries. This corresponds to
  running `python planet.py -x config.ini`.
+ Blacklisting . By selecting one or more of the entries in the list
  of entries, and clicking the "Blacklist" button, you can stop these
  items from displaying on the planet. This is very useful for quickly
  blocking inappropriate or malformed content from your planet. Note
  that blacklisting does not take effect until you refresh or rerun the
  planet . (Blacklisting can also be done manually on the server by
  moving files from the cache directory to the blacklist directory.)


Installing the administration interface securely requires some
knowledge of web server configuration.

The admin interface consists of two parts: the admin template file and
the server callback script. Both must be correctly installed for the
administration interface to work.



Installing the admin template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The admin page template is found in `themes/common/admin.html.tmpl`.
This template needs to be added to your config file along with your
other templates, and optionally customized. Make sure that
`action="admin_cb.py"` found in several places in the file points to
the URL (or relative URL) of the admin callback script below.


Installing the admin callback script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The admin callback script, admin_cb.py, needs to be copied to
somewhere among your web server files. Depending on the details of
your web server, your permissions, etc., this can be done in several
different ways and in different places. There are three steps
involved:


#. Configuring the script
#. Enabling CGI
#. Secure access




Configuring the script
``````````````````````

At the top of the script, there are four variables you must customize.
The correct values of the first three variables can be found by
analyzing how you normally run the `planet.py` script. If you
typically run planet from within the working directory `BASE_DIR`,
using a command like `python [VENUS_INSTALL]/planet.py [CONFIG_FILE]`
you know all three values.

: `BASE_DIR`: This variable must contain the directory from where you
  usually run the planet.py script, to ensure that relative file names
  in the config files work correctly.
: `VENUS_INSTALL`: This variable must contain your venus installation
  directory, relative to BASE_DIR above.
: `CONFIG_FILE`: This variable must contain your configuration file,
  relative to BASE_DIR above.
: `ADMIN_URL`: This variable must contain the URL (or relative URL) of
  the administration page, relative to this script's URL.




Enabling CGI
````````````

You will need to ensure that it can be run as a CGI script. This is
done differently on different web server platforms, but there are at
least three common patterns


+ **Apache with .htaccess**. If your server allows you to use
  `.htaccess` files, you can simply add `Options +ExecCGI AddHandler
  cgi-script .py` in an .htaccess file in the planet output directory to
  enable the server to run the script. In this case, the admin_cb.py
  file can be put alongside the rest of the planet output files.
+ **Apache without .htaccess**. If your server does not allow you to
  add CGI handlers to `.htaccess` files, you can add `Options +ExecCGI
  AddHandler cgi-script .py` to the relevant part of the central apache
  configuration files.
+ **Apache with cgi-bin**. If your server only allow CGI handlers in
  pre-defined directories, you can place the `admin_cb.py` file there,
  and make sure to update the `action="admin_cb.py"` code in the
  template file `admin.html.tmpl`, as well as the `ADMIN_URL` in the
  callback script.


In all cases, it is necessary to make sure that the script is executed
as the same user that owns the planet output files and the cache.
Either the planet output is owned by the apache user (usually `www-
data`), or Apache's `suexec`_ feature can be used to run the script as
the right user.



Securing the admin interface
````````````````````````````

If you don't want every user to be able to administrate your planet,
you must secure at least the `admin_cb.py` file, and preferrably the
`admin.html` file as well. This can be done using your web server's
regular access control features. See `here`_ for Apache documentation.

.. _here: http://httpd.apache.org/docs/2.0/howto/auth.html
.. _suexec: http://httpd.apache.org/docs/2.0/suexec.html


