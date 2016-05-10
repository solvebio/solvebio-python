import os
import hashlib
import binascii

# Default thresholds for multipart S3 files
MULTIPART_THRESHOLD = 64 * 1024 * 1024
MULTIPART_CHUNKSIZE = 64 * 1024 * 1024


def md5sum(path, multipart_threshold=MULTIPART_THRESHOLD,
           multipart_chunksize=MULTIPART_CHUNKSIZE):

    def _read_chunks(f, chunk_size):
        chunk = f.read(chunk_size)
        while chunk:
            yield chunk
            chunk = f.read(chunk_size)

    filesize = os.path.getsize(path)

    with open(path, "rb") as f:
        if multipart_threshold and filesize > multipart_threshold:
            block_count = 0
            md5string = ""
            for block in _read_chunks(f, multipart_chunksize):
                md5 = hashlib.md5()
                md5.update(block)
                md5string += md5.hexdigest()
                block_count += 1

            md5 = hashlib.md5()
            md5.update(binascii.unhexlify(md5string))
        else:
            block_count = None
            md5 = hashlib.md5()
            for block in _read_chunks(f, multipart_chunksize):
                md5.update(block)

    return md5.hexdigest(), block_count
