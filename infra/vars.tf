variable "source_uri" {
  description = "s3://source-bucket/path/within/bucket"
}

variable "dest_uri" {
  description = "s3://dest-bucket/path/within/bucket"
}

variable "region" {
  description = "aws region where both buckets are located in"
}
