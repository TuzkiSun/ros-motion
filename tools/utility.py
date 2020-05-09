# Copyright 2019 Shanghai Fangling Computer Software Co. Ltd. All rights reserved.
# Author: Miaocheng Yu (miaochengyu@fLcnc.com)
#
# Change Logs:
# Date           Author           Notes
# 2019-07-31     Miaocheng Yu     Some script utilities.

import glob
import os
import requests
from SCons.Script import *

def is_windows():
    return os.name == 'nt'

def mkdir(path):
    """mkdir() create the folder if not exist.

    Args:
      path specifies the dest directory to create.
    """
    try:
        os.mkdir(path)
    except Exception:
        pass
    else:
        print('{0} is created.'.format(path))

def get_subdirs(abs_path_dir, recursive=False):
    lst = [os.path.join(abs_path_dir, n)
        for n in os.listdir(abs_path_dir)
            if os.path.isdir(os.path.join(abs_path_dir, n)) and n[0] != '.']

    if not recursive:
        return lst

    subs = lst
    for d in lst:
        subs.extend(get_subdirs(d,  recursive))

    return subs

def get_tools_nodes(env):
    """get_tools_nodes() will return nodes in tools folder.

    After change config files in tools, a rebuild usually is required.
    This method will return file as Node type.
    """
    module_dir = os.path.dirname(os.path.abspath(__file__))
    nodes = Glob(os.path.join(module_dir, '*.py'))

    subdirs = get_subdirs(module_dir, True)
    EXCLUDE = os.path.join(module_dir, 'boards')

    for d in subdirs:
        if d[0: len(EXCLUDE)] == EXCLUDE:
            # tools/boards folder only works under rtos mode.
            if env['rtos']:
                nodes.extend(Glob(os.path.join(d, '*.py')))
                nodes.extend(Glob(os.path.join(d, '*.ld')))
            else:
                continue
        else:
            nodes.extend(Glob(os.path.join(d, '*.py')))
    return nodes

def is_msvc(env):
    """is_msvc() test whether compiler is msvc

    """
    return is_windows() and not env['rtos'] and 'default' == env['TOOLS'][0]

def is_native_mingw(env):
    """is_native_mingw() test whether env configs mingw for windows(NOT rtos)

    """
    return not env['rtos'] and 'mingw' == env['TOOLS'][0]

def is_cross_mingw(env):
    """is_cross_mingw() test whether env configs mingw for rtos

    """
    return env['rtos'] and 'mingw' == env['TOOLS'][0]

def download_file(src_url_path, src_file, dst_path, dst_file = ""):
    if not dst_file:
        dst_file = src_file
    dst = os.path.join(dst_path, dst_file)
    if not os.path.exists(dst):
        url = src_url_path + '/' + src_file
        r = requests.get(url)
        if r.status_code >= 300:
            print(r.text)
            return
        with open(dst, "wb") as f:
            f.write(r.content)

def update_vscode_config(base_url):
    """update_vscode_config() downloads vscode config files.
    
    Args:
        base_url: http://dev.eng.flcnc.com/app/vsc-conf/<xxxxxx>/<Vx.y.z.XXXXXXXX>
                 Please refer to http://gitlab.eng.flcnc.com/devtools/vsc-conf get corrent url.
                 Example: http://dev.eng.flcnc.com/app/vsc-conf/icut-mk/V0.0.1.04fb9ebb/
    """
    dst_dir = '.vscode'
    mkdir(dst_dir)
    try:
        url = base_url + "vscode"
        if base_url[-1] != '/':
            url = base_url + '/' + "vscode"
        download_file(url, "settings.json", dst_dir)
        download_file(url, "tasks.json", dst_dir)
        download_file(url, "launch.json", dst_dir)
    except Exception as e:
        print("Some error occurs while download from {0}".format(url))
        print("Error: ", e)

def copy_to_build(env, file):
    """copy_to_build() used to copy file from source to build dir.

    In Variant_dir mode, files are copyed automaticly. Use copy_to_build() to do a copy.
    CAUTION: This copy is not perform immedietaly.
    Args:
        file: the relative path to SConscript.
    Return:
        An environment builder node.
    """
    return env.Command(file, File(file).srcnode(), Copy("$TARGET", "$SOURCE"))
