#remove all entries with Yahoo! Pipes error
import sys

data = sys.stdin.read()
if data.find('No such pipe, or this pipe has been deleted') < 0:
  sys.stdout.write(data)
