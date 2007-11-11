# portalocker.py - Cross-platform (posix/nt) API for flock-style file locking.
#                  Requires python 1.5.2 or better.
# See http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65203/index_txt
# Except where otherwise noted, recipes in the Python Cookbook are 
# published under the Python license.

"""Cross-platform (posix/nt) API for flock-style file locking.

Synopsis:

   import portalocker
   file = open("somefile", "r+")
   portalocker.lock(file, portalocker.LOCK_EX)
   file.seek(12)
   file.write("foo")
   file.close()

If you know what you're doing, you may choose to

   portalocker.unlock(file)

before closing the file, but why?

Methods:

   lock( file, flags )
   unlock( file )

Constants:

   LOCK_EX
   LOCK_SH
   LOCK_NB

I learned the win32 technique for locking files from sample code
provided by John Nielsen <nielsenjf@my-deja.com> in the documentation
that accompanies the win32 modules.

Author: Jonathan Feinberg <jdf@pobox.com>
Version: $Id: portalocker.py,v 1.3 2001/05/29 18:47:55 Administrator Exp $
"""

import os

if os.name == 'nt':
	import win32con
	import win32file
	import pywintypes
	LOCK_EX = win32con.LOCKFILE_EXCLUSIVE_LOCK
	LOCK_SH = 0 # the default
	LOCK_NB = win32con.LOCKFILE_FAIL_IMMEDIATELY
	# is there any reason not to reuse the following structure?
	__overlapped = pywintypes.OVERLAPPED()
elif os.name == 'posix':
	import fcntl
	LOCK_EX = fcntl.LOCK_EX
	LOCK_SH = fcntl.LOCK_SH
	LOCK_NB = fcntl.LOCK_NB
else:
	raise RuntimeError("PortaLocker only defined for nt and posix platforms")

if os.name == 'nt':
	def lock(file, flags):
		hfile = win32file._get_osfhandle(file.fileno())
		win32file.LockFileEx(hfile, flags, 0, -0x10000, __overlapped)

	def unlock(file):
		hfile = win32file._get_osfhandle(file.fileno())
		win32file.UnlockFileEx(hfile, 0, -0x10000, __overlapped)

elif os.name =='posix':
	def lock(file, flags):
		fcntl.flock(file.fileno(), flags)

	def unlock(file):
		fcntl.flock(file.fileno(), fcntl.LOCK_UN)

if __name__ == '__main__':
	from time import time, strftime, localtime
	import sys
	import portalocker

	log = open('log.txt', "a+")
	portalocker.lock(log, portalocker.LOCK_EX)

	timestamp = strftime("%m/%d/%Y %H:%M:%S\n", localtime(time()))
	log.write( timestamp )

	print "Wrote lines. Hit enter to release lock."
	dummy = sys.stdin.readline()

	log.close()

