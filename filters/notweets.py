#remove all tweets
import sys

data = sys.stdin.read()
if data.find('<id>tag:twitter.com,') < 0:
  sys.stdout.write(data)
