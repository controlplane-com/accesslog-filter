region = "eu-central-1"

source_uri = "s3://julian-log-router-test/cpln-test/"

# AWS advises agains using the same bucket for input/output of a function
dest_uri = "s3://julian-log-router-filtered/access-logs-only"
