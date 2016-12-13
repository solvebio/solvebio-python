def check_gzip(file_path):
    """Check if we have a gzipped file"""
    try:
        with open(file_path, 'rb') as temp:
            magic_check = temp.read(2)
            if magic_check != '\037\213':
                return False
            else:
                return True
    except:
        return False

    return False
