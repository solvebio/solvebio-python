import mimetypes


def check_gzip_path(file_path):
    """Check if we have a gzipped file path"""
    _, ftype = mimetypes.guess_type(file_path)
    return ftype == 'gzip'
