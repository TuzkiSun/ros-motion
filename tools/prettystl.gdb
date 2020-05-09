# Copyright 2019 Shanghai Fangling Computer Software Co. Ltd. All rights reserved.
# Author: Miaocheng Yu (miaochengyu@fLcnc.com)

# Refer: https://stackoverflow.com/questions/4985414/how-to-enable-gdb-pretty-printing-for-c-stl-objects-in-eclipse-cdt

# TODO(miaochengyu): Test and fix error under Linux!!!

python
import sys, os, glob
def execCmd(cmd):  
    r = os.popen(cmd)  
    text = r.read()  
    r.close()  
    return text

cmd = "which gdb"
if os.name == 'nt':
    cmd = "where gdb"

gdb_path = execCmd(cmd)
config_path = os.path.join(os.path.dirname(gdb_path), '../share/gcc-?.?.?/python/libstdcxx/v6')
pathes = glob.glob(config_path)
if len(pathes):
    sys.path.insert(0, pathes[0])
    from printers import register_libstdcxx_printers
    register_libstdcxx_printers (None)
else:
    print('No gdb python printer found!')
end
