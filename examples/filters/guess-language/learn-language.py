#!/usr/bin/env python
"""A filter to guess languages.

This utility saves a Trigram object on file.

(See the REAME file for more details).

Requires Python 2.1, recommends 2.4.
"""
__authors__ = [ "Eric van der Vlist <vdv@dyomedea.com>"]
__license__ = "Python"

from trigram import Trigram
from sys import argv
from cPickle import dump


def main():
    tri = Trigram(argv[1])
    out = open(argv[2], 'w')
    dump(tri, out)
    out.close()

if __name__ == '__main__':
    main()
