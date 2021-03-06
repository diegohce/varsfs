#import logging

import os
import resource
import subprocess
from errno import ENOENT, EPERM
from stat import S_IFDIR, S_IFREG
from time import time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn


class FileNode:

	def __init__(self):
		self.name = ""
		self.getter_fn = None
		self.setter_fn = None
		self.attrs = None
		self.fd = None
##
#

class Helpers:

	started_at = 0

	@staticmethod
	def get_pid(varname):
		return '%d' % os.getpid()

	@staticmethod
	def get_user(varname):
		return os.environ['LOGNAME']

	@staticmethod
	def get_uptime(varname):
		return '%f' % (time() - Helpers.started_at)

	@staticmethod
	def get_no_file(varname):
		soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
		return '%d\t%d' % (soft, hard)

	@staticmethod
	def get_fd_count(varname):
		out = subprocess.check_output('ls /proc/self/fd |wc -l', shell=True)
		return out

##
#

#class VarsFS(LoggingMixIn, Operations):
class VarsFS(Operations):

	def __init__(self, mountpoint):
		self.mountpoint = mountpoint
		self.files = {}
		self.fd = 3
		self.uid = os.getuid()
		now = time()

		Helpers.started_at = time()

		root = FileNode()
		root.name = '/'
		root.attrs = dict(st_mode=(S_IFDIR | 0o755), st_ctime=now,
							   st_mtime=now, st_atime=now, st_nlink=2,
                               st_uid=self.uid)
		self.files[''] = root


	def __create_defaults(self):
		self.Add('uptime', Helpers.get_uptime)
		self.Add('user', Helpers.get_user)
		self.Add('pid', Helpers.get_pid)
		self.Add('file-limits', Helpers.get_no_file)
		self.Add('fd-count', Helpers.get_fd_count)


	def Add(self, varname, getter_fn, setter_fn=None):
		f = FileNode()
		f.name = varname
		f.getter_fn = getter_fn
		f.setter_fn = setter_fn

		mode = 0o664
		if setter_fn is None:
			mode = 0o444

		f.attrs = dict(st_mode=(S_IFREG | mode), st_nlink=1,
					   st_size=0, st_ctime=time(), st_mtime=time(),
					   st_atime=time(), st_uid=self.uid)
		self.files[varname] = f


	def getattr(self, path, fh=None):
		p = path[1:]
		if p not in self.files:
			raise FuseOSError(ENOENT)

		if self.files[p].getter_fn is not None:
			self.files[p].attrs['st_size'] = len(self.files[p].getter_fn(p))
		return self.files[p].attrs

	def open(self, path, flags):
		p = path[1:]

		if self.files[p].fd is None:
			self.fd += 1
			self.files[p].fd = self.fd
		return self.files[p].fd

	def read(self, path, size, offset, fh):
		p = path[1:]
		try:
			if self.files[p].getter_fn is None:
				raise FuseOSError(EPERM)
			return self.files[p].getter_fn(p)
		except KeyError:
			raise FuseOSError(ENOENT)
		

	def readdir(self, path, fh):
		return ['.', '..'] + [x for x in self.files if x != '']

	#def statfs(self, path):
	#	return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

	def write(self, path, data, offset, fh):
		p = path[1:]
		try:
			if self.files[p].setter_fn is None:
				raise FuseOSError(EPERM)
			self.files[p].setter_fn(p, data)
			return len(data)
		except KeyError:
			raise FuseOSError(ENOENT)

	def truncate(self, path, length, fh=None):
		pass


	def Run(self, foreground=True):
		#logging.basicConfig(level=logging.DEBUG)

		self.__create_defaults()

		if foreground:
			fuse = FUSE(self, self.mountpoint, foreground=foreground, nothreads=True)
		else:
			import threading
			def fn():
				#print "New thread"
				fuse = FUSE(self, self.mountpoint, foreground=True, nothreads=True)
			t = threading.Thread(target=fn)
			t.setDaemon(True)
			t.start()



