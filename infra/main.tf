locals {
  source_bucket_name = regex("s3://(.+?)/", "${var.source_uri}/")[0]
  dest_bucket_name   = regex("s3://(.+?)/", "${var.dest_uri}/")[0]

  source_prefix = regex("s3://(.+?)(/.*)", "${var.source_uri}/")[1]
}

resource "aws_iam_role" "lambda_role" {
  name = "accesslog-filter"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}


resource "aws_iam_role_policy" "s3_access" {
  name = "accesslog-filter"
  role = aws_iam_role.lambda_role.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "s3:Get*",
        "s3:Describe*",
        "s3:List*"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:s3:::${local.source_bucket_name}",
        "arn:aws:s3:::${local.source_bucket_name}/*"
      ]
    },
    {
      "Action": [
        "s3:Put*",
        "s3:Describe*",
        "s3:List*"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:s3:::${local.dest_bucket_name}",
        "arn:aws:s3:::${local.dest_bucket_name}/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

data "archive_file" "src" {
  type       = "zip"
  source_dir = "../src"

  output_path = "../accesslog-filter.zip"
}

resource "aws_lambda_function" "handler" {
  function_name    = "accesslog-filter"
  role             = aws_iam_role.lambda_role.arn
  handler          = "main.handler"
  runtime          = "python3.8"
  timeout          = 30
  filename         = "../accesslog-filter.zip"
  source_code_hash = data.archive_file.src.output_base64sha256

  environment {
    variables = {
      DEST_URI   = var.dest_uri
      SOURCE_URI = var.source_uri
    }
  }
}


# Adding S3 bucket as trigger to my lambda and giving the permissions
resource "aws_s3_bucket_notification" "trigger" {
  bucket = local.source_bucket_name
  lambda_function {
    lambda_function_arn = aws_lambda_function.handler.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "${trim(local.source_prefix, "/")}/"
  }
}


resource "aws_lambda_permission" "trigger" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.handler.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::${local.source_bucket_name}"
}
