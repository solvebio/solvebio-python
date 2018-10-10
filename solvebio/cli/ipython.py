from __future__ import absolute_import
import sys
import os


def _print(msg):
    """
    Handle Python 2 interactive shells without requiring
    new print() format.
    """
    sys.stdout.write(msg + '\n')


def launch_ipython_shell(args):  # pylint: disable=unused-argument
    """Open the SolveBio shell (IPython wrapper)"""
    try:
        import IPython  # noqa
    except ImportError:
        _print("The SolveBio Python shell requires IPython.\n"
               "To install, type: 'pip install ipython'")
        return False

    if hasattr(IPython, "version_info"):
        if IPython.version_info > (5, 0, 0, ''):
            return launch_ipython_5_shell(args)

    _print("WARNING: Please upgrade IPython (you are running version: {})"
           .format(IPython.__version__))
    return launch_ipython_legacy_shell(args)


def launch_ipython_5_shell(args):
    """Open the SolveBio shell (IPython wrapper) with IPython 5+"""
    import IPython  # noqa
    from traitlets.config import Config

    c = Config()
    path = os.path.dirname(os.path.abspath(__file__))

    try:
        # see if we're already inside IPython
        get_ipython  # pylint: disable=undefined-variable
        _print("WARNING: Running IPython within IPython.")
    except NameError:
        c.InteractiveShell.banner1 = 'SolveBio Python shell started.\n'

    c.InteractiveShellApp.exec_files = ['{}/ipython_init.py'.format(path)]
    IPython.start_ipython(argv=[], config=c)


def launch_ipython_legacy_shell(args):  # pylint: disable=unused-argument
    """Open the SolveBio shell (IPython wrapper) for older IPython versions"""
    try:
        from IPython.config.loader import Config
    except ImportError:
        _print("The SolveBio Python shell requires IPython.\n"
               "To install, type: 'pip install ipython'")
        return False

    try:
        # see if we're already inside IPython
        get_ipython  # pylint: disable=undefined-variable
    except NameError:
        cfg = Config()
        prompt_config = cfg.PromptManager
        prompt_config.in_template = '[SolveBio] In <\\#>: '
        prompt_config.in2_template = '   .\\D.: '
        prompt_config.out_template = 'Out<\\#>: '
        banner1 = '\nSolveBio Python shell started.'

        exit_msg = 'Quitting SolveBio shell.'
    else:
        _print("Running nested copies of IPython.")
        cfg = Config()
        banner1 = exit_msg = ''

    # First import the embeddable shell class
    try:
        from IPython.terminal.embed import InteractiveShellEmbed
    except ImportError:
        # pylint: disable=import-error,no-name-in-module
        from IPython.frontend.terminal.embed import InteractiveShellEmbed

    path = os.path.dirname(os.path.abspath(__file__))
    init_file = '{}/ipython_init.py'.format(path)
    exec(compile(open(init_file).read(), init_file, 'exec'),
         globals(), locals())

    InteractiveShellEmbed(config=cfg, banner1=banner1, exit_msg=exit_msg)()
