#!/usr/bin/env python
import glob, trace, unittest, os, sys

# start in a consistent, predictable location
os.chdir(sys.path[0])

# find all of the planet test modules
modules = map(trace.fullmodname, glob.glob(os.path.join('tests', 'test_*.py')))

# load all of the tests into a suite
suite = unittest.TestLoader().loadTestsFromNames(modules)

# run test suite
unittest.TextTestRunner().run(suite)
