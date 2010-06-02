#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import cgitb
cgitb.enable()

from urllib import unquote
import sys, os

# Modify this to point to where you usually run planet.
BASE_DIR = '..'

# Modify this to point to your venus installation dir, relative to planet dir above.
VENUS_INSTALL = "venus"

# Config file, relative to planet dir above
CONFIG_FILE = "config/live"

# Admin page URL, relative to this script's URL
ADMIN_URL = "admin.html"


# chdir to planet dir - config may be relative from there
os.chdir(os.path.abspath(BASE_DIR))

# Add venus to path.
sys.path.append(VENUS_INSTALL)

# Add shell dir to path - auto detection does not work
sys.path.append(os.path.join(VENUS_INSTALL, "planet", "shell"))

# import necessary planet items 
from planet import config
from planet.spider import filename


# Load config
config.load(CONFIG_FILE)

# parse query parameters
form = cgi.FieldStorage()


# Start HTML output at once
print "Content-Type: text/html;charset=utf-8"     # HTML is following
print                                             # blank line, end of headers


print '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
print '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="sv"><head><meta http-equiv="Content-Type" content="text/html;charset=utf-8" /><title>Admin results</title></head><body>'
print '<div>'

# Cache and blacklist dirs

cache = config.cache_directory()
blacklist = config.cache_blacklist_directory()

# Must have command parameter
if not "command" in form:
  print "<p>Unknown command</p>"

elif form['command'].value == "blacklist":


  # Create the blacklist dir if it does not exist
  if not os.path.exists(blacklist):
    os.mkdir(blacklist)
    print "<p>Created directory %s</p>" % blacklist
  
  # find list of urls, in the form bl[n]=url

  for key in form.keys():

    if not key.startswith("bl"): continue

    url = unquote(form[key].value)

    # find corresponding files
    cache_file = filename(cache, url)
    blacklist_file = filename(blacklist, url)

    # move to blacklist if found
    if os.path.exists(cache_file):

      os.rename(cache_file, blacklist_file)

      print "<p>Blacklisted <a href='%s'>%s</a></p>" % (url, url)

    else:

      print "<p>Unknown file: %s</p>" % cache_file

    print """
<p>Note that blacklisting does not automatically 
refresh the planet. You will need to either wait for
a scheduled planet run, or refresh manually from the admin interface.</p>
"""


elif form['command'].value == "run":

  # run spider and refresh

  from planet import spider, splice
  try:
     spider.spiderPlanet(only_if_new=False)
     print "<p>Successfully ran spider</p>"
  except Exception, e:
     print e

  doc = splice.splice()
  splice.apply(doc.toxml('utf-8'))

elif form['command'].value == "refresh":

  # only refresh

  from planet import splice

  doc = splice.splice()
  splice.apply(doc.toxml('utf-8'))

  print "<p>Successfully refreshed</p>"

elif form['command'].value == "expunge":

  # only expunge
  from planet import expunge
  expunge.expungeCache()

  print "<p>Successfully expunged</p>"




print "<p><strong><a href='" + ADMIN_URL + "'>Return</a> to admin interface</strong></p>"



print "</body></html>"
