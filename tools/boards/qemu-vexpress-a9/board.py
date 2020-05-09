# Copyright 2019 Shanghai Fangling Computer Software Co. Ltd. All rights reserved.
# Author: Miaocheng Yu (miaochengyu@fLcnc.com)
#
# Change Logs:
# Date           Author           Notes
# 2019-09-21     Miaocheng Yu     qemu vexexpress config.

import os
from SCons.Script import *

def config(env):
    # Process build options for compiler/linker
    device = (' -march=armv7-a -marm -msoft-float')

    ccflags = device + ' -Wall'
    asflags = ' -c' + device + ' -x assembler-with-cpp -D__ASSEMBLY__ -I.'
    lflags = device + ' -lm -lgcc -lc'
    lflags += ' -nostartfiles -Wl,--gc-sections,-Map=rtthread.map,-cref,-u,system_vectors '

    cxxflags = ' -Woverloaded-virtual -fno-exceptions -fno-rtti'

    flags = {'ASFLAGS': asflags.split(' ')}
    env.MergeFlags(flags)

    flags = {'CCFLAGS': ccflags.split(' ')}
    env.MergeFlags(flags)

    flags = {'CXXFLAGS': cxxflags.split(' ')}
    env.MergeFlags(flags)

    flags = {'LINKFLAGS': lflags.split(' ')}
    env.MergeFlags(flags)

    module_dir = os.path.dirname(os.path.abspath(__file__))
    f = ' -T %s' % (os.path.join(module_dir, env['memcfg']))
    flags = {'LINKFLAGS': f.split(' ')}
    env.MergeFlags(flags)
