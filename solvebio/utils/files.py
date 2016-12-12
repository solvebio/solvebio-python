def check_gzip(file_path):
    """Check if we have a gzipped file"""
    try:
        with open(file_path, "U") as temp:
            magic_check = temp.read(2)
            if magic_check != '\037\213':
                return False
    except:
        return False

    return True
