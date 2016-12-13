import mimetypes


def check_gzip_contents(file_path):
    """Check if we have a gzipped file path"""
    try:
        with open(file_path, 'rb') as temp:
            return temp.read(2) == '\037\213'
    except:
        pass

    return False


def check_gzip_path(file_path):
    """Check if we have a gzipped file path"""
    _, ftype = mimetypes.guess_type(file_path)
    return ftype == 'gzip'
