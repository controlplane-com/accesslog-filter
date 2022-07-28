# Accesslog filter

This project contains a small AWS lambda function + the necessary Terraform boilerplate to deploy it.

The function listens to S3 events from a source bucket, filters out irrelevant log events and finally persists the rest in a destination bucket.

It is usually used with Control Plane's `External Logs` feature when the external log sink is an S3 bucket.

# How to deploy

You need to pass terraform 3 variables. Consult the file `example.tfvars` for an example:

```terraform
region = "eu-central-1"

source_uri = "s3://julian-log-router-test/cpln-test/"

# AWS advises agains using the same bucket for input/output of a function
dest_uri = "s3://julian-log-router-filtered/access-logs-only"
```

- `region`: the region where both the source and destination bucket exist. This region will also host the lambda function.
- `source_uri`: an S3 path in the format `s3://bucket/path/to/what/ever`. Only files with this key prefix are considered. Used to filter by org.
- `dest_uri`: an S3 path in the format `s3://bucket/path/to/what/ever`. Files will end up here after filtering.

# Prerequisites

- At least Terraform 0.14
- Both buckets must exist. You probably want to setup retention policy anyway
- The role under which you run TF must be able to create Roles and Policies (IAM)

# What gets created under my account?

- A lambda function
- A role for the function (cloudwatch access, read access to source bucket, write access to dest bucket)
- A trigger on the source bucket connected to the lambda

# How are log files processed?

The processing just removes all logs where the container is not `_accesslog` but you are free to change it to suit your needs.
Since the format of the log files is always `jsonl`, a simple string search is used to detect matches thus saving CPU on JSON parsing.

An empty file is just not written to the destination bucket. In CloudWatch, you can recognize it easily:

```
2022-07-28T14:15:13.018+03:00	file prefix/my-org/2022/07/28/11/05/XrowrWy2.jsonl does not contain access logs
```

The lambda function tries its best to preserve the key structure of the processed files. For example if the input file is `{source_uri}/acme-org/2022/07/28/04/30/8Gdd2dwZ.jsonl`, then the resulting file will end up in `{dest_uri}/acme-org/2022/07/28/04/30/8Gdd2dwZ.jsonl`.

Files are gzipped (level 9) before uploading them to the destinatiob bucket.
