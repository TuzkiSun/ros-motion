# Copyright 2019 Shanghai Fangling Computer Software Co. Ltd. All rights reserved.
# Author: Miaocheng Yu (miaochengyu@fLcnc.com)
#
# Change Logs:
# Date           Author           Notes
# 2019-08-05     Miaocheng Yu     Custom builders.

import fnmatch
import os
from SCons.Script import *

def prepare_builder(env):
    """prepare_builder() will define custom builders.

    """
    pass

def export_headers(env, parent, pattern='*.h', recursive=True):
    """export_headers will export header files to export path.

    @param parent The folder path where to copy headers from.
           If parent is 'libalpha/src/add', and a header file 'add.h' contains.
           Then add.h will be copy to export/include/add/add.h
    @param pattern A pattern to identify the files that are headers.
    @param recursive Search recursively for headers.
    @return A list of Install() nodes.
    """
    DEST_INC_DIR = os.path.join(env.subst('$EXPORT_PATH'), 'include')
    parent = os.path.abspath(parent)
    if os.path.isfile(parent):
        parent = os.path.dirname(parent)

    parent = str(Entry(parent).srcnode())
    base_folder = os.path.basename(parent)
    return _export_headers_internal(env, parent, base_folder,
                                    DEST_INC_DIR, pattern, recursive)

def _export_headers_internal(env, parent, base_folder, dest_base,
                             pattern='*.h', recursive=True):

    """_export_headers_internal will export header files to export path.

    @param parent The folder path where to copy headers from.
           If parent is 'libalpha/src/add', and a header file 'add.h' contains.
           Then add.h will be copy to export/include/add/add.h
    @param base_folder The top folder name, in previous example, it is 'add'.
    @param dest_base The folder headers will copy to.
    @param pattern A pattern to identify the files that are headers.
    @param recursive Search recursively for headers.
    @return A list of Install() nodes.
    """
    nodes = []
    for entry in os.listdir(parent):
        entry_path = os.path.join(parent, entry)
        if os.path.isfile(entry_path) and fnmatch.fnmatch(entry, pattern):
            dest = entry_path[entry_path.find(base_folder): ]
            dest = os.path.dirname(dest) # Remove file name
            nodes.append(env.Install(os.path.join(dest_base, dest), entry_path))
        elif os.path.isdir(entry_path) and recursive:
            nodes.extend(_export_headers_internal(env, entry_path, base_folder,
                         dest_base, pattern, recursive))
    return nodes
