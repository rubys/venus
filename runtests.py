#!/usr/bin/env python
# coding=utf-8
import glob
import os
import sys
import unittest
from trace import fullmodname

# try to start in a consistent, predictable location
if sys.path[0]:
    os.chdir(sys.path[0])
sys.path[0] = os.getcwd()

# determine verbosity
verbosity = 1
for arg, value in (('-q', 0), ('--quiet', 0), ('-v', 2), ('--verbose', 2)):
    if arg in sys.argv:
        verbosity = value
        sys.argv.remove(arg)

# find all of the planet test modules
modules = []
for pattern in sys.argv[1:] or ['test_*.py']:
    modules += map(fullmodname, glob.glob(os.path.join('tests', pattern)))

# enable logging
import planet

if verbosity == 0:
    planet.getLogger("FATAL", None)
if verbosity == 1:
    planet.getLogger("WARNING", None)
if verbosity == 2:
    planet.getLogger("DEBUG", None)

# load all of the tests into a suite
try:
    suite = unittest.TestLoader().loadTestsFromNames(modules)
except Exception as exception:
    # attempt to produce a more specific message
    for each_module in modules:
        __import__(each_module)
    raise

# run test suite
unittest.TextTestRunner(verbosity=verbosity).run(suite)
