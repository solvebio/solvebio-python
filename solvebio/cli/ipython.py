from solvebio.credentials import get_credentials


def launch_ipython_shell(args):  # pylint: disable=unused-argument
    """Open the SolveBio shell (IPython wrapper)"""
    try:
        from IPython.config.loader import Config
    except ImportError:
        print("The SolveBio Python shell requires IPython.\n"
              "To install, type: 'pip install ipython'")

    try:
        # see if we're already inside IPython
        get_ipython  # pylint: disable=undefined-variable
    except NameError:
        cfg = Config()
        prompt_config = cfg.PromptManager
        prompt_config.in_template = '[SolveBio] In <\\#>: '
        prompt_config.in2_template = '   .\\D.: '
        prompt_config.out_template = 'Out<\\#>: '
        banner1 = 'SolveBio Python shell started.'
        creds = get_credentials()

        if creds:
            banner1 += "\nYou are logged in as {}".format(creds[0])
        else:
            banner1 += '\nYou are not logged in. Please run "solvebio login".'

        exit_msg = 'Quitting SolveBio shell.'
    else:
        print("Running nested copies of IPython.")
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
    from solvebio import (version, Depository, DepositoryVersion, Dataset,  # noqa
                          DatasetField, Query, PagingQuery, Filter,  # noqa
                          RangeFilter, Sample, Annotation, User)  # noqa

    from solvebio.cli.auth import login as login_with_args
    from solvebio.cli.auth import logout as logout_with_args
    from solvebio.cli.auth import whoami as whoami_with_args

    login = lambda args=None: login_with_args(args)  # noqa
    logout = lambda: logout_with_args(None)  # noqa
    whoami = lambda: whoami_with_args(None)  # noqa
    InteractiveShellEmbed(config=cfg, banner1=banner1, exit_msg=exit_msg)()
