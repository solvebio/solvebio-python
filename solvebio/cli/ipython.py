from __future__ import absolute_import
import sys


def _print(msg):
    """
    Handle Python 2 interactive shells without requiring
    new print() format.
    """
    sys.stdout.write(msg + '\n')


def launch_ipython_shell(args):  # pylint: disable=unused-argument
    """Open the SolveBio shell (IPython wrapper)"""
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

    # Now create an instance of the embeddable shell. The first
    # argument is a string with options exactly as you would type them
    # if you were starting IPython at the system command line. Any
    # parameters you want to define for configuration can thus be
    # specified here.

    # Add common solvebio classes and methods our namespace here so that
    # inside the ipython shell users don't have run imports
    import solvebio  # noqa
    from solvebio import *  # noqa
    from solvebio.utils.printing import pager  # noqa

    # Add some convenience functions to the interactive shell
    from solvebio.cli.auth import login, logout, whoami, get_credentials  # noqa

    # If an API key is set in solvebio.api_key, use that.
    # Otherwise, look for credentials in the local file,
    # Otherwise, ask the user to log in.
    if solvebio.api_key or get_credentials():
        _, solvebio.api_key = whoami()
    else:
        login()

    if not solvebio.api_key:
        _print("SolveBio requires a valid account. "
               "To sign up, visit: https://www.solvebio.com/signup")
        return

    InteractiveShellEmbed(config=cfg, banner1=banner1, exit_msg=exit_msg)()
