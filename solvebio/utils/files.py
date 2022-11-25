import mimetypes
import os

COMPRESSIONS = ('.gz', '.gzip', '.bz2', '.z', '.zip', '.bgz')


def separate_filename_extension(filename):
    """Separates filename into base name
    and extension while handling compressed
    filename extensions.

    Args:
        filename (str): A filename, can also
            be a full filepath.
    Returns:
        base name (str): Base filename (or path)
            without extension.
        extension (str): File extension beginning
            with leading period (e.g. '.txt').
        compression (str): Compression extension
            with leading period (e.x. '.gz').
    """
    base_filename, file_extension = os.path.splitext(filename)
    if file_extension in COMPRESSIONS and "." in base_filename:
        compression = file_extension
        base_filename, file_extension = os.path.splitext(base_filename)
    else:
        compression = ''
    return base_filename, file_extension, compression


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
