from urllib.parse import urlparse
import io

def get_bucket_and_key(s):
    u = urlparse(s)
    return (u.hostname, u.path.strip('/'))


def compute_key(filter_prefix, dest_path, object_key):
    if object_key.startswith(filter_prefix):
        object_key = object_key[len(filter_prefix):]
    else:
        return dest_path + '/' + object_key

    return dest_path + object_key


MARKER1 = b'"container":"_accesslog"'
MARKER2 = b'"container":"cpln-accesslog"'


def retain_accesslogs(dest, src):
    buf = io.BufferedReader(src)
    line = buf.readline()
    while line != b'':
        if MARKER1 in line or MARKER2 in line:
            dest.write(line)
        line = buf.readline()
