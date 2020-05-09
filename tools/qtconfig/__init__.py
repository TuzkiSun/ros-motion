# Copyright 2020 Shanghai Fangling Computer Software Co. Ltd. All rights reserved.
# Author: Miaocheng Yu (miaochengyu@fLcnc.com)
#
# Change Logs:
# Date           Author           Notes
# 2020-02-29     Miaocheng Yu     Configurations for qt4/5

import os
import re
import traceback
import utility
from SCons.Script import *

# System environment QTDIR specifies the target qt.
# By default:
#   Windows: 'C:/Qt/Qt5.12.7/5.12.7/mingw73_32'
#   Linux:   '/usr/local/Qt/Qt5.12.7/5.12.7/gcc_32'

def Uic(env, *arg, **kwarg):
    try:
        qt_ver = env['QT_VER']
    except Exception as e:
        print('Uic(): No qt specified, please call prepare_qt() first.', str(e))
        Exit(1)

    if qt_ver[0] == '4':
        return env.Uic4(*arg, **kwarg)
    else:
        return env.Uic5(*arg, **kwarg)

def Ts(env, *arg, **kwarg):
    try: qt_ver = env['QT_VER']
    except Exception as e:
        print('Ts(): No qt specified, please call prepare_qt() first.', str(e))
        Exit(1)
    if qt_ver[0] == '4':
        return env.Ts4(*arg, **kwarg)
    else:
        return env.Ts5(*arg, **kwarg)

def Qm(env, *arg, **kwarg):
    try: qt_ver = env['QT_VER']
    except Exception as e:
        print('Qm(): No qt specified, please call prepare_qt() first.', str(e))
        Exit(1)
    if qt_ver[0] == '4':
        return env.Qm4(*arg, **kwarg)
    else:
        return env.Qm5(*arg, **kwarg)

def pri_parse(pri_file):
    """ pri_parse() parse the specified pri_file.

        return:
          A dict contain src/head/ui/qrc files.
          {
              "HEADERS": ["xx.h", "zz/yy.h"],
              "SOURCES": [],
              "FORMS": [],
              "RESOURCES": [],
              "TRANSLATIONS": []
          }
    """
    catalog = ''
    catalog_pattern = r'^(HEADERS|SOURCES|FORMS|RESOURCES|TRANSLATIONS)'
    ret = {}
    try:
        with open(pri_file, 'r') as f:
            for l in f.readlines():
                line = l.strip()
                if line == '':
                    continue
                if line[0] == '#':
                    continue
                obj = re.search(catalog_pattern, line)
                if obj:
                    catalog = obj.group(1)
                    content = line[line.find('=') + 1:]
                    if ret.has_key(catalog):
                        ret[catalog] += (' ' + content)
                    else:
                        ret[catalog] = content
                else:
                    ret[catalog] += line
        for key in ret.keys():
            # 1, replace '\' as space
            ret[key] = ret[key].replace('\\', ' ')
            # 2, replace '$$PWD' as '.'
            ret[key]= ret[key].replace('$$PWD', '.')
            # 3, Split to list
            ret[key] = ret[key].split()
            print("1:", ret[key])
            print("2:", len(ret[key]))

        return ret

    except Exception as e:
        traceback.print_exc()
        print('Pri file not exist or with wrong format! Compile corrupted.')
        Exit(2)

def recursive_glob(base, pattern, exclude_pattern = ''):
    # CAUSION: SCons.Node.FS.Dir.isdir() not work!
    result = []
    for dir in Glob(str(base) + '/*'):
        if type(dir) is SCons.Node.FS.Dir:
            result.extend(recursive_glob(dir, pattern, exclude_pattern))

    for f in Glob(os.path.join(str(base), pattern), exclude = exclude_pattern):
        if type(f) is SCons.Node.FS.File:
           result.append(f)

    return result

def qrc_scan(node, env, path, arg):
    qrc_re = re.compile(r'.*<file>(.*)</file>.*')
    contents = node.get_text_contents()
    resources = qrc_re.findall(contents)

    base_path = os.path.dirname(node.rstr())
    return env.File(resources, directory=base_path)

def prepare_qt(env, **args):
    """ prepare_qt() perform the environment of qt building.

        **args contain:
          console = True/False, whether build a console application or gui application.
          moc_debug = True/False, whether to show verbose info of scons_qt or not.
    """
    qtdir = os.environ.get('QTDIR', '')
    debug = args.get('moc_debug', 0)
    console = args.get('console', 0)
    try:
        if utility.is_windows():
            if qtdir == '':
                qtdir = r'C:/Qt/Qt5.12.7/5.12.7/mingw73_32'
            prepare_qt_win(env, qtdir, moc_debug=debug, console=console)
        else:
            if qtdir == '':
                qtdir = r'/usr/local/Qt/Qt5.12.7/5.12.7/gcc_32'
            prepare_qt_linux(env, qtdir, moc_debug=debug, console=console)

        # qrc scanner
        qrcscan = Scanner(name = 'qrcfile',
                          function = qrc_scan,
                          argument = None,
                          skeys = ['.qrc'])

        env.Append(SCANNERS = qrcscan)

    except Exception as e:
        print('prepare_qt() failed! No qt config performed!')
        print('    Qt dir configs as:', qtdir)
        traceback.print_exc()

def prepare_qt_win(env, qtdir, **args):
    ver_pattern = r'.*(\d\.\d{1,2}\.\d{1,2}).*'
    obj = re.search(ver_pattern, qtdir)
    qt_ver = obj.group(1)
    env['QT_VER'] = qt_ver
    is_qt4 = qt_ver[0] == '4'
    is_mingw_ver = re.search(r'.*(mingw).*', qtdir) != None
    if is_mingw_ver:
        if env['msvc']:
            raise Exception('Please set correct QTDIR environment for msvc!')
        if re.search(r'.*(mingw.*_64).*', qtdir) != None:
            raise Exception('Only 32bit mingw qt is supported!')

    if is_qt4:
        if is_mingw_ver:
            raise Exception('Mingw version qt4 is not supported!')
        prepare_qt4_win_vs(env, qtdir, **args)
    else:
        if is_mingw_ver:
            prepare_qt5_win_mingw32(env, qtdir, **args)
        else:
            prepare_qt5_win_vs(env, qtdir, **args)

def prepare_qt4_win_vs(env, qtdir, **args):
    # TODO: qt4 version not compile tested yet.
    env['QT4DIR'] = qtdir
    env['CXXFILESUFFIX'] = '.cpp'
    env['QT4_DEBUG'] = args['moc_debug']
    env.Tool('qt4')
    # Enable default modules.
    env.EnableQt4Modules([ 'QtGui', 'QtCore' ], debug=env['debug'])

    env.Append(CPPPATH = [os.path.join(qtdir, 'mkspecs', 'win32-msvc2010')])
    env.Append(LIBPATH = os.path.join(qtdir, 'lib'))

    defines = 'UNICODE _UNICODE WIN32'
    defines += ' QT_DLL QT_HAVE_MMX QT_HAVE_3DNOW QT_HAVE_SSE QT_HAVE_MMXEXT QT_HAVE_SSE2 QT_THREAD_SUPPORT'

    if not env['debug']:
        defines += ' QT_NO_DEBUG'
    env.AppendUnique(CPPDEFINES = defines.split(' '))

    if not args['console']:
        env.AppendUnique(LINKFLAGS = ['/SUBSYSTEM:WINDOWS'])
    else:
        env.AppendUnique(LINKFLAGS = ['/SUBSYSTEM:CONSOLE'])

def prepare_qt5_win_mingw32(env, qtdir, **args):
    env['QT5DIR'] = qtdir
    env['CXXFILESUFFIX'] = '.cpp'
    env['QT5_DEBUG'] = args['moc_debug']
    env.Tool('qt5')
    # Enable default modules.
    env.EnableQt5Modules([ 'QtGui', 'QtCore', 'QtWidgets' ], debug=env['debug'])

    env.Append(CPPPATH = [os.path.join(qtdir, 'mkspecs', 'win32-g++')])
    env.Append(LIBPATH = os.path.join(qtdir, 'lib'))
    # CAUSION: libmingw32.a must link before libqtmain.a
    # So use Prepand() instead of Append()
    env.Prepend(LIBS = ['mingw32', 'shell32'])

    ccflags = ' -fno-keep-inline-dllexport -fexceptions -mthreads'
    flags = {'CCFLAGS': ccflags.split(' ')}
    env.MergeFlags(flags)

    lflags = ' -mthreads'
    if not args['console']:
        lflags += ' -Wl,-subsystem,windows'
    else:
        lflags += ' -Wl,-subsystem,console'

    flags = {'LINKFLAGS': lflags.split(' ')}
    env.MergeFlags(flags)

    defines = 'UNICODE _UNICODE WIN32 MINGW_HAS_SECURE_API=1'
    if not env['debug']:
        defines += ' QT_NO_DEBUG'
    else:
        defines += ' QT_QML_DEBUG'
    env.AppendUnique(CPPDEFINES = defines.split(' '))

def prepare_qt5_win_vs(env, qtdir, **args):
    raise Exception('VS2017 version qt5 is not supported yet!')

def prepare_qt_linux(env, qtdir, **args):
    ver_pattern = r'.*(\d\.\d{1,2}\.\d{1,2}).*'
    obj = re.search(ver_pattern, qtdir)
    qt_ver = obj.group(1)
    env['QT_VER'] = qt_ver
    is_qt4 = qt_ver[0] == '4'
    is_gcc_32 = re.search(r'.*(gcc_32).*', qtdir) != None
    if is_qt4:
        raise Exception('QT4 is not supported!')

    if is_gcc_32:
        prepare_qt5_linux_gcc32(env, qtdir, **args)
    else:
        prepare_qt5_linux_gcc64(env, qtdir, **args)

def prepare_qt5_linux_gcc32(env, qtdir, **args):
    env['QT5DIR'] = qtdir
    env['CXXFILESUFFIX'] = '.cpp'
    env['QT5_DEBUG'] = args['moc_debug']
    env.Tool('qt5')
    # Enable default modules.
    env.EnableQt5Modules([ 'QtGui', 'QtCore', 'QtWidgets' ], debug=env['debug'])

    env.Append(CPPPATH = [os.path.join(qtdir, 'mkspecs', 'linux-g++-32')])
    env.Append(LIBPATH = os.path.join(qtdir, 'lib'))

    ccflags = ' -m32'
    flags = {'CCFLAGS': ccflags.split(' ')}
    env.MergeFlags(flags)

    lflags = ' -m32'
    flags = {'LINKFLAGS': lflags.split(' ')}
    env.MergeFlags(flags)

    env.Prepend(LIBS = ['GL'])

    defines = '_REENTRANT'
    if not env['debug']:
        defines += ' QT_NO_DEBUG'
    else:
        defines += ' QT_QML_DEBUG'
    env.AppendUnique(CPPDEFINES = defines.split(' '))

def prepare_qt5_linux_gcc64(env, qtdir, **args):
    env['QT5DIR'] = qtdir
    env['CXXFILESUFFIX'] = '.cpp'
    env['QT5_DEBUG'] = args['moc_debug']
    env.Tool('qt5')
    # Enable default modules.
    env.EnableQt5Modules([ 'QtGui', 'QtCore', 'QtWidgets' ], debug=env['debug'])

    env.Append(CPPPATH = [os.path.join(qtdir, 'mkspecs', 'linux-g++-64')])
    env.Append(LIBPATH = os.path.join(qtdir, 'lib'))

    env.Prepend(LIBS = ['GL'])

    defines = '_REENTRANT'
    if not env['debug']:
        defines += ' QT_NO_DEBUG'
    else:
        defines += ' QT_QML_DEBUG'
    env.AppendUnique(CPPDEFINES = defines.split(' '))
