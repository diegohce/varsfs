# VarsFS

Application variables filesystem

# What is it?

So far it's a python library, based on fusepy library, that allows you to expose whatever value you want from your app,
tipically metrics or config values, as files in a directory. 

Files can be read-only or read-write(able).

# Usage
  
  * See [requirements.txt](https://github.com/diegohce/varsfs/blob/master/requirements.txt) for required libraries.
  
  * Check [main.py](https://github.com/diegohce/varsfs/blob/master/main.py) for a working example.

# API

## VarsFS object

```#python
VarsFS(mountpoint)
```
Takes only one argument; the fullpath to the mount point. Returns a new instance of VarsFS.

### Add(varname, getter_fn, setter_fn=None)

Creates a "file" named as the value of ```varname``` into ```mountpoint```. 
Read operations will call the ```getter_fn``` and write operations will call ```setter_fn```.

*getter_fn* must be declared so to receive one argument (the variable name)
```
def some_getter(varname):
  ...
```

*setter_fn* must be declared so to receive two arguments (the variable name and the value to be assigned)
```
def some_setter(varname, data):
  ...
```

### Run(foreground=True)

Starts the file system. If ```foreground``` is set to False, will start the filesystem on a separated thread, 
otherwise will block execution.

