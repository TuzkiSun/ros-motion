# Copyright 2019 Shanghai Fangling Computer Software Co. Ltd. All rights reserved.
# Author: Miaocheng Yu (miaochengyu@fLcnc.com)
#
# Change Logs:
# Date           Author           Notes
# 2019-07-29     Miaocheng Yu     Projects template script.

import os
import re
import sys

# Step 1: Clone tools from gitlab.
def get_user_name():
    try:
        with open('.git/config', 'r') as f:
            content = f.read()

        pattern = r'http://(.+)@gitlab'
        objs = re.search(pattern, content)
        return objs.group(1)

    except Exception as e:
        print('Fail to get user name for: ', e)
        print('Use default user name "miaochengyu"')

    return 'miaochengyu'

def _clone_from_git(user_name, proj_path, proj_name, commit, local_path):
    if not os.path.exists(local_path):
        # TODO(miaochengyu): change the gitlab path to right one.
        if os.system(
            "git clone http://{0}@gitlab-2.eng.flcnc.com/scons/{1}.git {2}".
            format(user_name, proj_path, local_path)) != 0:

            return False

        if os.system("cd {0} && git checkout -b workspace {1}".
                     format(local_path, commit)) != 0:

            return False

    return True

try:
    in_integrate = os.path.exists('../SolutionMagicFile')
    user_name = get_user_name()
    tools_path = 'tools'
    if in_integrate:
        tools_path = '../' + tools_path
    proj_name = os.path.basename(tools_path)
    if not _clone_from_git(user_name, proj_name, proj_name, 'master', tools_path):
        raise Exception("Clone '{0}' failed, build is existing...".format(proj_name))
except Exception as e:
    print(e)
    sys.exit(1)

# Step 2: Base environment
cwd = os.path.normpath(os.getcwd())
sys.path.insert(0, os.path.join(cwd, tools_path))

import optconfig
(t, v) = optconfig.get_tools()
env = Environment(ENV = os.environ,
                  tools = t,
                  MSVC_VERSION = v, # This not works while msvc not in command
                  IN_INTEGRATE = in_integrate, # Specifies a solution or a solo project.
                  CALL_FROM_INTEGRATE = False,
                  PROJ_NAMES = [os.path.basename(cwd)],
                  # ROOT_DIR specifies integrate dir in integrate mode.
                  # otherwise, it is same to project SConstruct dir.
                  ROOT_DIR = os.path.normpath(os.path.join(cwd, '..'))
                             if in_integrate else cwd,
                  OPT_FILE = 'options.py')

# Step 3: Process options

# option config
optconfig.prepare_opts(env)

# prepare builders
import builder
builder.prepare_builder(env)

# Prepare os(compiler)
import compiler_config
compiler_config.prepare_env(env)

# Step 4: Prepare board
if env['rtos']:
    import boards.board_config as board

    board.prepare_board(env)

build = env.subst('$BUILD_PATH')
if in_integrate:
    build = os.path.join(build, os.path.basename(cwd))

# For solo project, always add libpath.
compiler_config.config_solo_prj_libpath(env, build)

SConscript('SConscript', exports = 'env', variant_dir = build, duplicate = 0)
# clean variant dir while rebuild or clean
Clean('.', build)
