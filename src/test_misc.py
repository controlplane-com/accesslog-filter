import io
import unittest
from urllib.parse import urlparse
from botocore.response import StreamingBody
import misc


class Testmisc(unittest.TestCase):
    def test_parse(self):
        res = misc.get_bucket_and_key(
            "s3://julian-log-router-test/cpln-test/")
        self.assertEqual("julian-log-router-test", res[0])
        self.assertEqual("cpln-test", res[1])

    def test_parse2(self):
        res = misc.get_bucket_and_key("s3://julian-log-router-test/cpln-test")
        self.assertEqual("julian-log-router-test", res[0])
        self.assertEqual("cpln-test", res[1])

    def test_compute_path(self):
        res = misc.compute_key(
            "cpln-test", "hello", "cpln-test/coke/2022/03/17/13/23/rcirn3dZ.jsonl")
        self.assertEqual("hello/coke/2022/03/17/13/23/rcirn3dZ.jsonl", res)

    def test_compute_path_mismamtch(self):
        res = misc.compute_key(
            "cpln-test", "hello", "examples/coke/2022/03/17/13/23/rcirn3dZ.jsonl")
        self.assertEqual(
            "hello/examples/coke/2022/03/17/13/23/rcirn3dZ.jsonl", res)

    def test_full(self):
        (dest_bucket, dest_path) = misc.get_bucket_and_key(
            "s3://julian-log-router-filtered/access-logs-only")
        (_, source_prefix) = misc.get_bucket_and_key(
            "s3://julian-log-router-test/cpln-test/")

        res = misc.compute_key(source_prefix, dest_path,
                               "cpln-test/coke/2022/03/17/13/23/rcirn3dZ.jsonl")
        self.assertEqual(
            "access-logs-only/coke/2022/03/17/13/23/rcirn3dZ.jsonl", res)

    def xtest_filter_no_logs(self):
        sample = """line 1
line2
{"line": 3}
"""
        body = StreamingBody(
            io.BytesIO(bytes(sample, 'ascii')),
            len(sample)
        )

        dest = io.BytesIO()
        misc.retain_accesslogs(dest, body)

        self.assertEqual(0, dest.tell())

    def xtest_filter_only_logs(self):
        sample = """
{"timestamp":"2022-07-27T14:24:31.221Z","labels":{"provider":"aws","replica":"a56f6b93-bf6c-480c-a4db-2b3d20027e53","stream":"stdout","version":"2","workload":"jfrog","container":"_accesslog","gvc":"demo","location":"aws-eu-central-1"},"line":"Get \"http://127.0.0.1:8080/\": dial tcp 127.0.0.1:8080: connect: connection refused"}
{"timestamp":"2022-07-27T14:24:32.135Z","labels":{"version":"2","workload":"sleep","container":"_accesslog","gvc":"demo","location":"aws-us-west-2","provider":"aws","replica":"9ac11d1e-4221-4064-a78c-71c1372f408f","stream":"stdout"},"line":"Get \"http://127.0.0.1:8080/\": dial tcp 127.0.0.1:8080: connect: connection refused"}
"""
        body = StreamingBody(
            io.BytesIO(bytes(sample, 'ascii')),
            len(sample)
        )

        dest = io.BytesIO()
        misc.retain_accesslogs(dest, body)

        self.assertEqual(3, len(str(dest.getvalue(), 'ascii').split('\n')))

    def xtest_filter_some_logs(self):
        sample = """
{"timestamp":"2022-07-27T14:24:31.221Z","labels":{"provider":"aws","replica":"a56f6b93-bf6c-480c-a4db-2b3d20027e53","stream":"stdout","version":"2","workload":"jfrog","container":"_accesslog","gvc":"demo","location":"aws-eu-central-1"},"line":"Get \"http://127.0.0.1:8080/\": dial tcp 127.0.0.1:8080: connect: connection refused"}
junk
more junk
{"timestamp":"2022-07-27T14:24:32.135Z","labels":{"version":"2","workload":"sleep","container":"HELLO_","gvc":"demo","location":"aws-us-west-2"}
{"timestamp":"2022-07-27T14:24:32.135Z","labels":{"version":"2","workload":"sleep","container":"_accesslog","gvc":"demo","location":"aws-us-west-2","provider":"aws","replica":"9ac11d1e-4221-4064-a78c-71c1372f408f","stream":"stdout"},"line":"Get \"http://127.0.0.1:8080/\": dial tcp 127.0.0.1:8080: connect: connection refused"}
"""
        body = StreamingBody(
            io.BytesIO(bytes(sample, 'ascii')),
            len(sample)
        )

        dest = io.BytesIO()
        misc.retain_accesslogs(dest, body)

        self.assertEqual(3, len(str(dest.getvalue(), 'ascii').split('\n')))
