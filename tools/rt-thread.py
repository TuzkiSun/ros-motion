# Copyright 2019 Shanghai Fangling Computer Software Co. Ltd. All rights reserved.
# Author: Miaocheng Yu (miaochengyu@fLcnc.com)
#
# Change Logs:
# Date           Author           Notes
# 2019-10-06     Miaocheng Yu     Configurations for rt thread.
#                                 This config should only used while "rtos=1 rtos_os=rt_thread"

import os
import sys
from SCons.Script import *

def rtos_config(env):
    custom_opt = os.path.join(env['ROOT_DIR'], env['OPT_FILE'])
    vars = Variables(custom_opt, ARGUMENTS)

    vars.Add(PathVariable('rtt_bsp_root', 'Path to rtt bsp source folder',
                          '',
                          PathVariable.PathIsDir))
    vars.Update(env)
    Help(vars.GenerateHelpText(env))

    bsp_root = env['rtt_bsp_root']
    sys.path = sys.path + [bsp_root]

    # Exceptions will be processed in optconfig while call this module.
    # So we just process it as all is ok.
    import rtua
    # There are two type of rtt source code.
    # One type is a dist src folder, which RTT_ROOT is under BSP_ROOT
    # Another is a bsp integrate src folder.
    rtt_root = os.path.join(bsp_root, 'rt-thread')
    if not os.path.exists(rtt_root):
        rtt_root = os.path.join(bsp_root, '../..')

    cpp_path = rtua.GetCPPPATH(bsp_root, rtt_root)
    cpp_path_without_cpp = [ x for x in cpp_path if r'cplusplus' not in x]
    env.Prepend(CPPPATH = cpp_path_without_cpp)

    cpp_defines = rtua.GetCPPDEFINES()
    env.AppendUnique(CPPDEFINES = cpp_defines)
