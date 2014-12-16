import sys
from pydoc import plain
from ..utils.tabulate import tabulate

import solvebio


def all_datasets():
    datasets(latest='')


def datasets(**kwargs):
    """
    Lists all the datasets in tabulated form, page by page.
    """
    def get_page(page, **kwargs):
        depos = solvebio.Dataset.all(limit=100, page=page, **kwargs)
        fields = ['full_name', 'depository', 'title', 'description']
        headers = ['Name', 'Depository', 'Title', 'Description']
        return (tabulate([[d[i] for i in fields] for d in depos.data],
                         headers=headers, sort=True),
                depos.links['next'])

    try:
        import tty
        fd = sys.stdin.fileno()
        old = tty.tcgetattr(fd)
        tty.setcbreak(fd)
        getchar = lambda: sys.stdin.read(1)
    except (ImportError, AttributeError):
        tty = None
        getchar = lambda: sys.stdin.readline()[:-1][:1]

    filters = {'latest': kwargs.get('latest', True)}

    try:
        page = 1
        text, has_next = get_page(page, **filters)
        sys.stdout.write(text + '\n')

        while has_next:
            sys.stdout.write('-- More --')
            sys.stdout.flush()
            c = getchar()
            page += 1
            text, has_next = get_page(page, **filters)

            if c in ('q', 'Q'):
                sys.stdout.write('\r          \r')
                break

            sys.stdout.write('\n' + plain(text) + '\n')
    finally:
        if tty:
            tty.tcsetattr(fd, tty.TCSAFLUSH, old)
