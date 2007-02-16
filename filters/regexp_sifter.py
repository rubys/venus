import sys, re

# parse options
options = dict(zip(sys.argv[1::2],sys.argv[2::2]))

# read entry
doc = data = sys.stdin.read()

# Apply a sequence of patterns which turn a normalized Atom entry into
# a stream of text, after removal of non-human metadata.
for pattern,replacement in [
  (re.compile('<id>.*?</id>'),' '),
  (re.compile('<url>.*?</url>'),' '),
  (re.compile('<source>.*?</source>'),' '),
  (re.compile('<updated.*?</updated>'),' '),
  (re.compile('<published.*?</published>'),' '),
  (re.compile('<link .*?>'),' '),
  (re.compile('''<[^>]* alt=['"]([^'"]*)['"].*?>'''),r' \1 '),
  (re.compile('''<[^>]* title=['"]([^'"]*)['"].*?>'''),r' \1 '),
  (re.compile('''<[^>]* label=['"]([^'"]*)['"].*?>'''),r' \1 '),
  (re.compile('''<[^>]* term=['"]([^'"]*)['"].*?>'''),r' \1 '),
  (re.compile('<.*?>'),' '),
  (re.compile('\s+'),' '),
  (re.compile('&gt;'),'>'),
  (re.compile('&lt;'),'<'),
  (re.compile('&apos;'),"'"),
  (re.compile('&quot;'),'"'),
  (re.compile('&amp;'),'&'),
  (re.compile('\s+'),' ')
]:
  data=pattern.sub(replacement,data)

# process requirements
if options.has_key('--require'):
  for regexp in options['--require'].split('\n'):
     if regexp and not re.search(regexp,data): sys.exit(1)

# process exclusions
if options.has_key('--exclude'):
  for regexp in options['--exclude'].split('\n'):
     if regexp and re.search(regexp,data): sys.exit(1)

# if we get this far, the feed is to be included
print doc
