#!/usr/bin/env python
import glob, unittest, os, sys

# python 2.2 accomodations
try:
    from trace import fullmodname
except:
    def fullmodname(path):
        return os.path.splitext(path)[0].replace(os.sep, '.')

# more python 2.2 accomodations
if not hasattr(unittest.TestCase, 'assertTrue'):
    unittest.TestCase.assertTrue = unittest.TestCase.assert_
if not hasattr(unittest.TestCase, 'assertFalse'):
    unittest.TestCase.assertFalse = unittest.TestCase.failIf

# try to start in a consistent, predictable location
if sys.path[0]: os.chdir(sys.path[0])
sys.path[0] = os.getcwd()

# determine verbosity
verbosity = 1
for arg,value in (('-q',0),('--quiet',0),('-v',2),('--verbose',2)):
    if arg in sys.argv: 
        verbosity = value
        sys.argv.remove(arg)

# find all of the planet test modules
modules = []
for pattern in sys.argv[1:] or ['test_*.py']:
    modules += map(fullmodname, glob.glob(os.path.join('tests', pattern)))

# enable logging
import planet
if verbosity == 0: planet.getLogger("FATAL",None)
if verbosity == 1: planet.getLogger("WARNING",None)
if verbosity == 2: planet.getLogger("DEBUG",None)

# load all of the tests into a suite
try:
    suite = unittest.TestLoader().loadTestsFromNames(modules)
except Exception, exception:
    # attempt to produce a more specific message
    for module in modules: __import__(module)
    raise

# run test suite
unittest.TextTestRunner(verbosity=verbosity).run(suite)
