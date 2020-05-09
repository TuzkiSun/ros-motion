# Copyright 2019 Shanghai Fangling Computer Software Co. Ltd. All rights reserved.
# Author: Miaocheng Yu (miaochengyu@fLcnc.com)
#
# Change Logs:
# Date           Author           Notes
# 2019-08-02     Miaocheng Yu     RTOS board configs.

import importlib
import glob
import os
from SCons.Script import *

def prepare_board(env):
    """prepare_board() will update board related build config.

    This only works on rtos.
    """
    if not env['rtos']:
        pass

    # Board enum
    custom_opt = os.path.join(env['ROOT_DIR'], env['OPT_FILE'])
    vars = Variables(custom_opt, ARGUMENTS)

    module_dir = os.path.dirname(os.path.abspath(__file__))
    pathes = glob.glob(os.path.join(module_dir, '*/board.py'))

    board_names = []
    for path in pathes:
        folder = os.path.basename(os.path.dirname(path))
        board_names.append(folder)

    if len(board_names) == 0:
        print(('No board config found under tools/boards, '
               'cannot build rtos binaries.'))

        env.Exit(1)

    enum_map = {str(x): board_names[x] for x in range(len(board_names))}
    vars.Add(EnumVariable('board',
                          ('Set board while build for rtos.\n'
                            '    Use index instead of board name is allowed.'),
                          board_names[0],
                          allowed_values = tuple(board_names),
                          ignorecase = 2,
                          map = enum_map))

    vars.Update(env)
    env.Append(CPPDEFINES = {'BOARD': '"$board"'})

    # Memcfg file (*.ld) enum
    files = glob.glob(os.path.join(module_dir,
                                   '{0}/*.ld'.format(env['board'])))

    ld_files = []
    for f in files:
        ld_files.append(os.path.basename(f))

    if len(ld_files) == 0:
        print(('No board memory config file(*.ld) found, '
               'cannot build rtos binaries.'))

        env.Exit(1)

    enum_map = {str(x): ld_files[x] for x in range(len(ld_files))}
    vars.Add(EnumVariable('memcfg',
                          'Set ld file for board {0}'.format(__name__),
                          ld_files[0],
                          allowed_values = tuple(ld_files),
                          ignorecase = 2,
                          map = enum_map))

    vars.Update(env)

    Help(vars.GenerateHelpText(env))

    # Call board specified scripts set in cmd line board=xxxx
    board_module = importlib.import_module(
        'boards.{0}.board'.format(env['board']))

    board_module.config(env)
