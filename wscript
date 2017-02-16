#! /usr/bin/env python
# encoding: utf-8

import os
import sys

import waflib

top = '.'

def resolve(ctx):

    ctx.add_dependency(
        name='waf',
        recurse=False,
        optional=False,
        resolver='git',
        method='checkout',
        checkout='waf-1.9.7',
        sources=['github.com/waf-project/waf.git'])

    ctx.add_dependency(
        name='python-semver',
        recurse=False,
        optional=False,
        resolver='git',
        method='checkout',
        checkout='2.4.1',
        sources=['github.com/k-bx/python-semver.git'])

    ctx.add_dependency(
        name='shutilwhich',
        recurse=False,
        optional=False,
        resolver='git',
        method='checkout',
        checkout='1.1.0',
        sources=['github.com/mbr/shutilwhich.git'])

    # Testing dependencies
    ctx.add_dependency(
        name='tox',
        recurse=False,
        optional=False,
        resolver='git',
        method='checkout',
        checkout='2.6.0',
        sources=['github.com/tox-dev/tox.git'])

    ctx.add_dependency(
        name='pluggy',
        recurse=False,
        optional=False,
        resolver='git',
        method='checkout',
        checkout='0.4.0',
        sources=['github.com/pytest-dev/pluggy.git'])

    # Testing dependencies

    # ctx.add_dependency(
    #     name='pytest',
    #     recurse=False,
    #     optional=False,
    #     resolver='git',
    #     method='checkout',
    #     checkout='3.0.6',
    #     sources=['github.com/pytest-dev/pytest.git'])
    #
    ctx.add_dependency(
        name='py',
        recurse=False,
        optional=False,
        resolver='git',
        method='checkout',
        checkout='1.4.32',
        sources=['github.com/pytest-dev/py.git'])

    ctx.add_dependency(
        name='virtualenv',
        recurse=False,
        optional=False,
        resolver='git',
        method='checkout',
        checkout='15.1.0',
        sources=['github.com/pypa/virtualenv.git'])
    #
    # ctx.add_dependency(
    #     name='mock',
    #     recurse=False,
    #     optional=False,
    #     resolver='git',
    #     method='checkout',
    #     checkout='2.0.0',
    #     sources=['github.com/testing-cabal/mock.git'])
    #
    # ctx.add_dependency(
    #     name='pbr',
    #     recurse=False,
    #     optional=False,
    #     resolver='git',
    #     method='checkout',
    #     checkout='1.10.0',
    #     sources=['github.com/openstack-dev/pbr.git'])
    #
    # ctx.add_dependency(
    #     name='funcsigs',
    #     recurse=False,
    #     optional=False,
    #     resolver='git',
    #     method='checkout',
    #     checkout='0.4',
    #     sources=['github.com/aliles/funcsigs.git'])
    #
    # ctx.add_dependency(
    #     name='six',
    #     recurse=False,
    #     optional=False,
    #     resolver='git',
    #     method='checkout',
    #     checkout='4141a3e',
    #     sources=['github.com/benjaminp/six.git'])

def options(opt):

    opt.add_option('--skip_tests', default=False,
        action='store_true', help='Skip running unit tests')

    opt.add_option('--use_tox', default=False,
        action='store_true', help='Run unit tests using tox')


def configure(conf):

    # Ensure that the waf-light program is available in the in the
    # waf folder. This is used to build the waf binary.
    conf.find_program('waf-light', exts='',
        path_list=[conf.dependency_path('waf')])

    # Make sure we tox used for running unit tests
    conf.find_program('tox', mandatory=False)

def build_waf_binary(tsk):
    """
    Task for building the waf binary.
    """

    # Get the working directory
    # Waf checks whether a path is a waflib.Node or string by checking
    # isinstance(str) but in python3 most string are unicode, which makes the
    # test fail.
    wd = str(getattr(tsk, 'cwd', None))

    # Tools dir
    tools_dir = getattr(tsk.generator, 'tools_dir', None)
    tools_dir = [os.path.abspath(os.path.expanduser(d)) for d in tools_dir]

    # Run with ./waf --zones wurf to see the print
    waflib.Logs.debug("wurf: tools_dir={}".format(tools_dir))

    # Get the absolute path to all the tools (passed as input to the task)
    tool_paths = [t.abspath() for t in tsk.inputs] + tools_dir
    tool_paths = ','.join(tool_paths)

    # The prelude option
    prelude = '\timport waflib.extras.wurf.waf_entry_point'

    # Build the command to execute
    command = 'python waf-light configure build --make-waf --prelude="{}" '\
        '--tools={}'.format(prelude, tool_paths)

    # Get the waf BuildContext
    bld = tsk.generator.bld
    bld.cmd_and_log(command, cwd=wd, quiet=waflib.Context.BOTH)

    # Copy the waf binary to the build folder
    waf_src = bld.root.find_resource(os.path.join(wd, 'waf'))
    waf_dest = bld.bldnode.make_node('waf')
    waf_dest.write(waf_src.read('rb'), 'wb')

def build(bld):

    # Waf checks that source files are available when we create the
    # different tasks. We can ask waf to lazily do this because the waf
    # binary is not created until after we run the waf-light build
    # step. This is manipulated using the post_mode.
    bld.post_mode = waflib.Build.POST_LAZY

    # We need to invoke the waf-light from within the third_party/waf
    # folder as waf-light will look for wscript in the folder where the
    # executable was started - so we need to start it from the right
    # folder. Using cwd we can make sure the python process is lauched in
    # the right directory.


    tools_dir = [os.path.join(bld.dependency_path('shutilwhich'), 'shutilwhich'),
                 os.path.join(bld.dependency_path('python-semver'), 'semver.py'),
                 'src/wurf']

    bld(rule=build_waf_binary,
        cwd=bld.dependency_path('waf'),
        tools_dir=tools_dir,
        always=True)

    bld.add_group()

    if not bld.options.skip_tests:

        if bld.options.use_tox:
            _tox(bld=bld)
        else:
            _pytest(bld=bld)


# def _pytest(bld):
#
#     python_path = [bld.dependency_path('pytest'),
#                    bld.dependency_path('py'),
#                    bld.dependency_path('mock'),
#                    bld.dependency_path('pbr'),
#                    bld.dependency_path('funcsigs'),
#                    bld.dependency_path('six'),
#                    bld.dependency_path('shutilwhich'),
#                    bld.dependency_path('python-semver'),
#                    os.path.join(os.getcwd(),'src')]
#
#     bld_env = bld.env.derive()
#     bld_env.env = dict(os.environ)
#
#     separator = ';' if sys.platform == 'win32' else ':'
#     bld_env.env.update({'PYTHONPATH': separator.join(python_path)})
#
#     bld(rule='python -m pytest test',
#         cwd=bld.path,
#         env=bld_env,
#         always=True)

def _pytest(bld):

    python_path = [bld.dependency_path('tox'),
                   bld.dependency_path('pluggy'),
                   bld.dependency_path('py'),
                   bld.dependency_path('virtualenv'),
                   bld.dependency_path('shutilwhich'),
                   bld.dependency_path('python-semver'),
                   os.path.join(os.getcwd(),'src')]

    bld_env = bld.env.derive()
    bld_env.env = dict(os.environ)

    separator = ';' if sys.platform == 'win32' else ':'
    bld_env.env.update({'PYTHONPATH': separator.join(python_path)})

    bld(rule='python -m tox',
        cwd=bld.path,
        env=bld_env,
        always=True)


def _tox(bld):

    # Invoke tox to run all the pure Python unit tests. Tox creates
    # virtualenvs for different setups and runs unit tests in them. See the
    # tox.ini to see the configuration used and see
    # https://tox.readthedocs.org/ for more information about tox.
    #
    # We run tox at the end since we will use the freshly built waf binary
    # in some of the tests.
    #
    if not bld.env.TOX:
        bld.fatal("tox not found - re-run configure.")

    bld_env = bld.env.derive()
    bld_env.env = dict(os.environ)

    semver_path = bld.dependency_path('python-semver')
    shutil_path = bld.dependency_path('shutilwhich')
    wurf_path = os.path.join(os.getcwd(), 'src')

    bld_env.env.update({'PYTHONPATH': ':'.join(
        [wurf_path, semver_path, shutil_path])})

    bld(rule='tox', env=bld_env, always=True)
