

from varsfs import VarsFS


lname = "Cena\n"
fname = "Diego\n"

def get_fname(varname):
	global fname
	return fname

def get_lname(varname):
	global lname
	return lname

def set_lname(varname, data):
	global lname
	lname = data

if __name__ == '__main__':

	vfs = VarsFS('mnt')
	vfs.Add('fname', get_fname)
	vfs.Add('lname', get_lname, set_lname)
	vfs.Run(True)




