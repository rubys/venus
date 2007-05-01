import sys
from genshi.input import XMLParser
from genshi.output import HTMLSerializer

print ''.join(HTMLSerializer()(XMLParser(sys.stdin))).encode('utf-8')
