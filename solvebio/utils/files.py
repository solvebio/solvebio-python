import mimetypes


def check_gzip_path(file_path):
    """Check if we have a gzipped file path"""
    _, ftype = mimetypes.guess_type(file_path)
    return ftype == 'gzip'


def get_home_dir():
    try:
        # Python 3.5+
        from pathlib import Path
        return str(Path.home())
    except:
        from os.path import expanduser
        return expanduser("~")
