# Copyright 2019 Shanghai Fangling Computer Software Co. Ltd. All rights reserved.
# Author: Miaocheng Yu (miaochengyu@fLcnc.com)
#
# Change Logs:
# Date           Author           Notes
# 2019-08-01     Miaocheng Yu     scons opts config.

import importlib
import os
import sys
import utility
from SCons.Script import *

def get_tools():
    """get_tools() will detemine which compiler would use.
    """
    keys = ARGUMENTS.keys()
    msvc_ver = ARGUMENTS.get('msvc', '')
    if utility.is_windows():
        if msvc_ver and 'rtos' in keys:
            print('Rtos cannot build with msvc compiler!')
            Exit(1)
        if not msvc_ver:
            return (['mingw'], msvc_ver)
    return (['default'], msvc_ver)

def prepare_opts(env):
    """prepare_opts() will process command line options and add to env.

    Option 'rtos': Add option rtos=yes/no to command line to generate
                   rtos binary or not.
    Option 'rtos_os': Add option rtos_os=rt-thread/freertos to command line to specify
                      rtos type. This option only works while rtos=1.
    Option 'debug': Add option debug=yes/no to command line to build
                    debug/release version.
    Option 'define': Add macros to build, same to gcc option -D, this option
                     can be multi-set.
    Option 'incdir': Add additional include path of depends, this option can
                     be multi-set.
    Option 'libdir': Add additional library path of depends, this option can
                     be multi-set.
    """
    custom_opt = os.path.join(env['ROOT_DIR'], env['OPT_FILE'])
    vars = Variables(custom_opt, ARGUMENTS)

    if utility.is_windows():
        vc_versions = {
            '': '',
            'VS2017': '14.1',
            'VS2015': '14.0',
            'VS2010': '10.0',
            'VS2010Express': '10.0Exp',
            'VS2005': '8.0',
            'VS2005Express': '8.0Exp',
        }

        vars.Add(EnumVariable('msvc',
                            ('Set use msvc version and specifies vs version.'),
                            '',
                            allowed_values = tuple(vc_versions.values()),
                            ignorecase = 2))

    else:
        env['msvc'] = ''

    vars.Add(BoolVariable('rtos', 'Set to build rtos binaries', 0))
    vars.Add(BoolVariable('debug', 'Set to build debug version', 0))
    vars.Add(PathVariable('depends', 'Path to depends folder', os.path.join('$ROOT_DIR', 'depends'),
                          PathVariable.PathIsDirCreate))

    vars.Add(PathVariable('essentials', 'Path to essentials folder', os.path.join('$ROOT_DIR', 'essentials'),
                          PathVariable.PathIsDirCreate))

    vars.Add(PathVariable('build_path', 'Path to build folder', os.path.join('$ROOT_DIR', 'build'),
                          PathVariable.PathIsDirCreate))
    vars.Add(PathVariable('export_path', 'Path to export folder', os.path.join('$ROOT_DIR', 'export'),
                          PathVariable.PathIsDirCreate))

    vars.Update(env)

    cpp_defines = []
    for key, value in ARGLIST:
        if key == 'define':
            cpp_defines.append(value)

    incdirs = []
    for key, value in ARGLIST:
        if key == 'incdir':
            if os.path.isdir(value):
                incdirs.append(value)
            else:
                print("WARNING: incdir {0} does NOT exist!".format(value))

    libdirs = []
    for key, value in ARGLIST:
        if key == 'libdir':
            if os.path.isdir(value):
                libdirs.append(value)
            else:
                print("WARNING: libdir {0} does NOT exist!".format(value))

    if env['debug']:
        cpp_defines.extend(['DBG', 'DEBUG'])
    else:
        cpp_defines.append('NDEBUG')

    if utility.is_windows():
        cpp_defines.append('WIN32')

    if env['rtos']:
        cpp_defines.append('RTOS')
        os_types = {'rt-thread': 'RTOS_RTT',
                    'freertos': 'RTOS_FREERTOS',
                   }

        keys = os_types.keys()
        vars.Add(EnumVariable('rtos_os',
                          'Set rtos type.\n',
                          keys[1],
                          allowed_values = tuple(keys),
                          ignorecase = 2))

        vars.Update(env)
        cpp_defines.append(os_types[env['rtos_os']])

        print("Default use rt-thread as rtos. Use 'rtos_os=' variable to change!")

        try:
            # Call rtos specified scripts.
            rtos_module = importlib.import_module(env['rtos_os'])
            rtos_module.rtos_config(env)
        except Exception as e:
            print('Fail to do rtos specified config in {0}.py'.format(env['rtos_os']))
            print(e)
            sys.exit(1)

    env.AppendUnique(CPPDEFINES = cpp_defines)
    env.Replace(DEPENDS = '$depends')
    env.Replace(ESSENTIALS = '$essentials')
    env.Replace(EXPORT_PATH = '$export_path')
    # if integrate solution project, use build/ as variant dir
    # else use build/project_name as variant dir
    build_conf = 'debug' if env['debug'] else 'release'
    if File('SolutionMagicFile', '#').exists():
        env.Replace(BUILD_PATH = os.path.join('$build_path', build_conf))
    else:
        solo_sln_name = os.path.basename(Dir('#').abspath)
        env.Replace(BUILD_PATH = os.path.join('$build_path', build_conf, solo_sln_name))

    env.Append(CPPPATH = [os.path.join(env['DEPENDS'], 'include'),
                          os.path.join(env['ESSENTIALS'], 'include')])

    env.Append(CPPPATH = incdirs)

    env.Append(LIBPATH = [os.path.join(env['DEPENDS'], 'lib'),
                          os.path.join(env['ESSENTIALS'], 'lib')])

    env.Append(LIBPATH = libdirs)

    env.PrependENVPath('PATH', [os.path.join(env['DEPENDS'], 'bin'),
                                os.path.join(env['ESSENTIALS'], 'bin')])

    Help(vars.GenerateHelpText(env))

    env['TEST'] = 'test' in COMMAND_LINE_TARGETS
