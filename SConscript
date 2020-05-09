# Copyright 2019 Shanghai Fangling Computer Software Co. Ltd. All rights reserved.
# Author: Miaocheng Yu (miaochengyu@fLcnc.com)
#
# Change Logs:
# Date           Author           Notes
# 2019-08-04     Miaocheng Yu     SConscript file for libalpha projects.

Import('env')

SConscript('src/Sconscript', exports = 'env')
if env['TEST']:
    SConscript('tests/Sconscript', exports = 'env')
