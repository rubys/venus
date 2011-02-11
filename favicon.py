import sys, socket
from planet import config, feedparser
from planet.spider import filename
from urllib2 import urlopen
from urlparse import urljoin
from html5lib import html5parser, treebuilders
from ConfigParser import ConfigParser

# load config files (default: config.ini)
for arg in sys.argv[1:]:
  config.load(arg)
if len(sys.argv) == 1:
  config.load('config.ini')

from Queue import Queue
from threading import Thread

# determine which subscriptions have no icon but do have a html page
fetch_queue = Queue()
html = ['text/html', 'application/xhtml+xml']
sources = config.cache_sources_directory()
for sub in config.subscriptions():
  data=feedparser.parse(filename(sources,sub))
  if data.feed.get('icon'): continue
  if not data.feed.get('links'): continue
  for link in data.feed.links:
    if link.rel=='alternate' and link.type in html:
      fetch_queue.put((sub, link.href))
      break

# find the favicon for a given webpage
def favicon(page):
  parser=html5parser.HTMLParser(tree=treebuilders.getTreeBuilder('dom'))
  doc=parser.parse(urlopen(page))
  favicon = urljoin(page, '/favicon.ico')
  for link in doc.getElementsByTagName('link'):
    if link.hasAttribute('rel') and link.hasAttribute('href'):
      if 'icon' in link.attributes['rel'].value.lower().split(' '):
        favicon = urljoin(page, link.attributes['href'].value)
  if urlopen(favicon).info()['content-length'] != '0':
    return favicon

# thread worker that fills in the dictionary which maps subs to favicon
icons = {}
def fetch(thread_index, fetch_queue, icons):
  while 1: 
    sub, html = fetch_queue.get()
    if not html: break
    try:
      icon = favicon(html)
      if icon: icons[sub] = icon
    except:
      pass

# set timeout
try:
  socket.setdefaulttimeout(float(config.feed_timeout()))
except:
  pass

# (optionally) spawn threads, fetch pages
threads = {}
if int(config.spider_threads()):
  for i in range(int(config.spider_threads())):
    threads[i] = Thread(target=fetch, args=(i, fetch_queue, icons))
    fetch_queue.put((None, None))
    threads[i].start()
  for i in range(int(config.spider_threads())):
    threads[i].join()
else:
  fetch_queue.put((None, None))
  fetch(0, fetch_queue, icons)

# produce config file
config = ConfigParser()
for sub, icon in icons.items():
  config.add_section(sub)
  config.set(sub, 'favicon', icon)
config.write(sys.stdout)
