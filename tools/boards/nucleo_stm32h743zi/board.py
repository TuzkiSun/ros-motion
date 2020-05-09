# Copyright 2019 Shanghai Fangling Computer Software Co. Ltd. All rights reserved.
# Author: Miaocheng Yu (miaochengyu@fLcnc.com)
#
# Change Logs:
# Date           Author           Notes
# 2019-08-02     Miaocheng Yu     nucleo_stm32h743zi config.

import os
from SCons.Script import *

def config(env):
    # Process build options for compiler/linker
    device = (' -mcpu=cortex-m7 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard '
              '-ffunction-sections -fdata-sections')

    ccflags = device + ' -Wall -DSTM32H743xx -DUSE_HAL_DRIVER -D__ASSEMBLY__ '
    asflags = ' -c' + device + ' -x assembler-with-cpp -Wa,-mimplicit-it=thumb '
    lflags = device + ' -lm -lgcc -lc'
    lflags += ' -nostartfiles -Wl,--gc-sections,-cref,-u,Reset_Handler '

    cxxflags = ' -Woverloaded-virtual -fno-exceptions -fno-rtti '

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
