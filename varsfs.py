#import logging

from errno import ENOENT, EPERM
from stat import S_IFDIR, S_IFLNK, S_IFREG
from time import time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn


class FileNode:

	def __init__(self):
		self.name = ""
		self.getter_fn = None
		self.setter_fn = None
		self.attrs = None
	

#class VarsFS(LoggingMixIn, Operations):
class VarsFS(Operations):

	def __init__(self, mountpoint):
		self.mountpoint = mountpoint
		self.files = {}
		self.fd = 0
		now = time()

		root = FileNode()
		root.name = '/'
		root.attrs = dict(st_mode=(S_IFDIR | 0o755), st_ctime=now,
							   st_mtime=now, st_atime=now, st_nlink=2)
		self.files[''] = root


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
					   st_atime=time())
		self.files[varname] = f


	def getattr(self, path, fh=None):
		p = path[1:]
		if p not in self.files:
			raise FuseOSError(ENOENT)

		if self.files[p].getter_fn is not None:
			self.files[p].attrs['st_size'] = len(self.files[p].getter_fn(p))
		return self.files[p].attrs

	def open(self, path, flags):
		self.fd += 1
		return self.fd

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

	def statfs(self, path):
		return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

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
		fuse = FUSE(self, self.mountpoint, foreground=foreground)















