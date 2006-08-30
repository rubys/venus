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

# find all of the planet test modules
modules = map(fullmodname, glob.glob(os.path.join('tests', 'test_*.py')))

# load all of the tests into a suite
suite = unittest.TestLoader().loadTestsFromNames(modules)

# run test suite
unittest.TextTestRunner().run(suite)
