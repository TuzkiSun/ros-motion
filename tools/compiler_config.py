# Copyright 2019 Shanghai Fangling Computer Software Co. Ltd. All rights reserved.
# Author: Miaocheng Yu (miaochengyu@fLcnc.com)
#
# Change Logs:
# Date           Author           Notes
# 2019-08-01     Miaocheng Yu     Compiler related configs.

import builder
import os
import utility
from SCons.Script import *

def prepare_env(env):
    _prepare_cross_tool(env)

    if utility.is_msvc(env):
        _prepare_common_msvc_cfg(env)
    else:
        _prepare_common_gcc_cfg(env)

    # This only work while use mingw
    _mingw_static_link(env)

def _mingw_static_link(env):
    """_mingw_static_link() will set MingW built program static link libs.

    MingW usually requires libgcc_s_dw2-1.dll and libstdc++-6.dll while release.
    Add -static-libgcc and -static-libstdc++ to static link these two library.
    Or just add -static to static link all mingw related libs.
    """
    if utility.is_native_mingw(env):
        flags = {'LINKFLAGS': '-static'.split(' ')}
        env.MergeFlags(flags)

def _prepare_cross_tool(env):
    """_prepare_cross_tool() will adjust tool chain according to os and rtos.

    If host is rtos, "arm-none-eabi-" will be used.
    If host is not rtos, gcc(mingw under windows) will be used.
    """
    if env['rtos']:
        custom_opt = os.path.join(env['ROOT_DIR'], env['OPT_FILE'])
        vars = Variables(custom_opt, ARGUMENTS)

        vars.Add('build', 'The compiler prefix of gcc.', 'arm-none-eabi-')
        vars.Update(env)
        Help(vars.GenerateHelpText(env))

        prefix = env['build']
        env['AS'] = prefix + env['AS']
        env['CC'] = prefix + env['CC']
        env['CXX'] = prefix + env['CXX']
        env['AR'] = prefix + env['AR']
        env['LINK'] = prefix + env['LINK']

def _prepare_common_msvc_cfg(env):
    """_prepare_common_msvc_cfg() will config common msvc configs.

       Refer: https://github.com/SCons/scons/wiki/MsvcIncrementalLinking
    """
    ccflags = '/nologo /Zm200 /Zc:wchar_t- /W3 /w44996 /WX'
    cxxflags = '/GR /EHsc /w34189'
    linkflags = '/DYNAMICBASE /NXCOMPAT /INCREMENTAL:NO'
    if not env['debug']:
        ccflags += ' /O2 /MD'
    else:
        ccflags += ' /MDd'
        linkflags += ' /DEBUG'
        env['CCPDBFLAGS'] = '/Zi /Fd${TARGET}.pdb'
        env['PDB'] = '${TARGET.base}.pdb'

    flags = {'CCFLAGS': ccflags.split(' ')}
    env.MergeFlags(flags)

    flags = {'CXXFLAGS': cxxflags.split(' ')}
    env.MergeFlags(flags)

    env.AppendUnique(LINKFLAGS = linkflags.split(' '))

def _prepare_common_gcc_cfg(env):
    """_prepare_common_gcc_cfg() will config common gcc configs.

    For example:
      -g option in debug mode.
      -Wall etc.
    """
    ccflags = ' -fPIC'
    asflags = ''
    if not env['debug']:
        ccflags += ' -O2 -Os'
    else:
        ccflags += ' -gdwarf-2 -O0'
        asflags += ' -gdwarf-2'

    ccflags += ' -Wall -Werror'

    flags = {'LINKFLAGS': '-fPIC'.split(' ')}
    env.MergeFlags(flags)

    flags = {'ASFLAGS': asflags.split(' ')}
    env.MergeFlags(flags)

    flags = {'CCFLAGS': ccflags.split(' ')}
    env.MergeFlags(flags)

    # This is more like a bug of scons.
    # Build shared library with link static library fails with error:
    #    Source file: %s is static and is not compatible with shared target: %s
    # Must set to 1
    env['STATIC_AND_SHARED_OBJECTS_ARE_THE_SAME'] = 1

def library_depends_config(env, depends):
    """library_depends_config() configs library and include file depends.

    Only depends in-solution contains in depends.
    Third party libraries should be put in 'essentials/' and 'depends/'
    @param depends Contains library info.
           For example:
           depend_libs = [
                ('libalpha/src', ['Add']),
           ]
           For integrate solution, ${BUILD_PATH}="build/debug":
                CPPPATH will prepend '${BUILD_PATH}/libalpha/src'
                LIBPATH will prepend '${BUILD_PATH}/libalpha/src/lib'
           For solo solution(no SolutionMagicFile file), ${BUILD_PATH}="build/debug/libalpha":
                CPPPATH will prepend '${BUILD_PATH}/../libalpha/src'
                LIBPATH will prepend '${BUILD_PATH}/../libalpha/src/lib'
           LIBS 'Add' will be always added.
    """
    for path, libs in depends:
        build_path = os.path.join(env['BUILD_PATH'], path)
        if not File('SolutionMagicFile', env['ROOT_DIR']).exists():
            # TODO: Use '..' depends on optconfig how to config solo project build path.
            #       It is really ugly.
            build_path = os.path.join(env['BUILD_PATH'], '..', path)
        env.PrependUnique(CPPPATH = build_path)
        env.PrependUnique(LIBPATH = os.path.join(build_path, 'lib'))
        # libs
        if env['debug']:
            libs = [x + 'd' for x in libs]
        env.PrependUnique(LIBS = libs)

def config_exe(env, target):
    """config_exe() will add Program() related configs.

    @param returns the binary path relative to project.
           For example, '../bin' means libalpha/src/add/bin/
    """
    if not utility.is_msvc(env):
        flags = {'LINKFLAGS': ' -no-pie -fno-pie'.split(' ')}
        env.MergeFlags(flags)
    env['BUILD_TYPE'] = 'EXE'
    out_path = '../bin'
    # Export binary
    bins = env.Glob(os.path.join(out_path, '*{0}*'.format(target)))
    export_bin = env.Install(os.path.join(env['EXPORT_PATH'], 'bin'), bins)
    env.Alias('export', export_bin)
    return out_path

def config_library(env, target):
    """config_library() will add StaticLibrary() related configs.

    @param returns the library path relative to project.
           For example, '../lib' means libalpha/src/add/lib/
    """
    if (not env['debug']) and (env['msvc'] != ""):
        flags = {'ARFLAGS': ' /LTCG'.split(' ')}
        env.MergeFlags(flags)
    env['BUILD_TYPE'] = 'LIB'
    out_path = '../lib'
    # For lib export headers
    export_headers = builder.export_headers(env, '.')
    env.Alias('export', export_headers)
    # Export libs
    libs = env.Glob(os.path.join(out_path, '*{0}*'.format(target)))
    export_lib = env.Install(os.path.join(env['EXPORT_PATH'], 'lib'), libs)
    env.Alias('export', export_lib)
    return out_path

def config_shared_library(env, target):
    """config_shared_library() will add SharedLibrary() related configs.

    @param returns the library path relative to project.
           For example, '../lib' means libalpha/src/add/lib/
    """
    env['BUILD_TYPE'] = 'SHLIB'
    out_path = '../lib'
    # For shlib export headers
    export_headers = builder.export_headers(env, '.')
    env.Alias('export', export_headers)
    # Export libs
    libs = env.Glob(os.path.join(out_path, '*{0}*'.format(target)))
    export_lib = env.Install(os.path.join(env['EXPORT_PATH'], 'lib'), libs)
    env.Alias('export', export_lib)
    return out_path

def config_solo_prj_libpath(env, build_path):
    """config_solo_prj_libpath() will process libpath of solo project.

    By default, build_path is like '#build'
    But for solo project, it is something like '#build/libalpha', the manual
      added libalpha make the output path is same to integrate projects.
    So the solo prj libpath has to be special processed.
    """
    env.PrependUnique(LIBPATH = os.path.join(build_path, 'src/lib'))
    if env['TEST']:
        env.PrependUnique(LIBPATH = os.path.join(build_path, 'tests/lib'))

def config_base_src_path(env):
    """config_base_src_path() config src path as cpppath

    This method must be called under "src" folder of project.
    For example, xxxx/libalpha/src
    """
    # We should NOT use os.getcwd() to fetch current folder path.
    # Use getcwd(), get the result of src folder(if first time build), xxx/libalpha/tests
    # Use Dir('.').abspath, always get the variant_dir, xxx/build/libalpha/tests
    cwd = Dir('.').abspath
    if os.path.basename(cwd) != 'src':
        print('config_base_src_path() must be called under src folder!')
        Exit(1)
    else:
        env.Prepend(CPPPATH = cwd)

def config_base_tests_path(env):
    """config_base_tests_path() config tests and src path as cpppath

    This method must be called under "tests" folder of project.
    For example, xxxx/libalpha/tests
    """
    # We should NOT use os.getcwd() to fetch current folder path.
    # Use getcwd(), get the result of src folder(if first time build), xxx/libalpha/tests
    # Use Dir('.').abspath, always get the variant_dir, xxx/build/libalpha/tests
    cwd = Dir('.').abspath
    if os.path.basename(cwd) != 'tests':
        print('config_base_tests_path() must be called under tests folder!')
        Exit(1)
    else:
        # Add tests and src path to cpppath
        env.Prepend(CPPPATH = cwd)
        # Add tests bin folder path as macro TEST_PRJ_BIN_PATH
        # For example xxx/build/iutility/tests/bin
        test_bin_path = os.path.normpath(os.path.join(cwd, 'bin')).replace('\\', '/')
        env.AppendUnique(CPPDEFINES = {'TEST_PRJ_BIN_PATH' : test_bin_path})

def config_gtest(env):
    gtest_libs = ['gtest', 'gmock']
    if not utility.is_msvc(env):
        gtest_libs.append('pthread')
    if utility.is_msvc(env) and env['debug']:
        gtest_libs = [x + 'd' for x in gtest_libs]

    env.Append(LIBS = gtest_libs)
