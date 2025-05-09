
provider "aws" {
  region = "eu-west-2"
}


resource "aws_iam_role" "lambda_execution_role" {
  name = "lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Effect    = "Allow"
        Sid       = ""
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_s3_policy" {
  name        = "lambda_s3_policy"
  description = "Allow Lambda functions to read and write to S3"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = ["s3:GetObject", "s3:PutObject"]
        Effect   = "Allow"
        Resource = [
          "arn:aws:s3:::obfuscator-tool--bucket/*",
          "arn:aws:s3:::obfuscated-files-bucket/*"
        ]
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "lambda_s3_policy_attachment" {
  policy_arn = aws_iam_policy.lambda_s3_policy.arn
  role       = aws_iam_role.lambda_execution_role.name
}


resource "aws_s3_bucket" "obfuscator_tool_bucket" {
  bucket = "obfuscator-tool--bucket"
}

resource "aws_s3_bucket" "obfuscated_files_bucket" {
  bucket = "obfuscated-files-bucket"
}

resource "aws_lambda_function" "csv_processor_function" {
  filename         = "./csv_handler.zip"
  function_name    = "csvProcessorFunction"
  role             = aws_iam_role.lambda_execution_role.arn
  handler          = "csv_handler.lambda_handler"
  runtime          = "python3.9"
  memory_size      = 128
  timeout          = 60
  environment {
    variables = {
      OUTPUT_BUCKET = "obfuscated-files-bucket"
    }
  }
}

resource "aws_lambda_function" "json_processor_function" {
  filename         = "./json_handler.zip"
  function_name    = "jsonProcessorFunction"
  role             = aws_iam_role.lambda_execution_role.arn
  handler          = "json_handler.lambda_handler"
  runtime          = "python3.9"
  memory_size      = 128
  timeout          = 60
  environment {
    variables = {
      OUTPUT_BUCKET = "obfuscated-files-bucket"
    }
  }
}

resource "aws_lambda_function" "parquet_processor_function" {
  filename         = "./parquet_handler.zip"
  function_name    = "parquetProcessorFunction"
  role             = aws_iam_role.lambda_execution_role.arn
  handler          = "parquet_handler.lambda_handler"
  runtime          = "python3.9"
  memory_size      = 128
  timeout          = 60
  environment {
    variables = {
      OUTPUT_BUCKET = "obfuscated-files-bucket"
    }
  }
}

resource "aws_lambda_permission" "csv_lambda_permission" {
  statement_id  = "AllowS3InvokeCSV"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.csv_processor_function.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.obfuscator_tool_bucket.arn
}


resource "aws_lambda_permission" "json_lambda_permission" {
  statement_id  = "AllowS3InvokeJSON"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.json_processor_function.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.obfuscator_tool_bucket.arn
}


resource "aws_lambda_permission" "parquet_lambda_permission" {
  statement_id  = "AllowS3InvokeParquet"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.parquet_processor_function.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.obfuscator_tool_bucket.arn
}

resource "aws_s3_bucket_notification" "csv_trigger" {
  bucket = aws_s3_bucket.obfuscator_tool_bucket.id

  lambda_function {
    events             = ["s3:ObjectCreated:*"]
    filter_suffix      = ".csv"
    lambda_function_arn = aws_lambda_function.csv_processor_function.arn
  }
  depends_on = [aws_lambda_permission.csv_lambda_permission]
}

resource "aws_s3_bucket_notification" "json_trigger" {
  bucket = aws_s3_bucket.obfuscator_tool_bucket.id

  lambda_function {
    events             = ["s3:ObjectCreated:*"]
    filter_suffix      = ".json"
    lambda_function_arn = aws_lambda_function.json_processor_function.arn
  }
  depends_on = [aws_lambda_permission.json_lambda_permission]
}

resource "aws_s3_bucket_notification" "parquet_trigger" {
  bucket = aws_s3_bucket.obfuscator_tool_bucket.id

  lambda_function {
    events             = ["s3:ObjectCreated:*"]
    filter_suffix      = ".parquet"
    lambda_function_arn = aws_lambda_function.parquet_processor_function.arn
  }
  depends_on = [aws_lambda_permission.parquet_lambda_permission]
}

output "obfuscator_tool_bucket_arn" {
  value = aws_s3_bucket.obfuscator_tool_bucket.arn
}

output "obfuscated_files_bucket_arn" {
  value = aws_s3_bucket.obfuscated_files_bucket.arn
}

output "csv_lambda_function_arn" {
  value = aws_lambda_function.csv_processor_function.arn
}

output "json_lambda_function_arn" {
  value = aws_lambda_function.json_processor_function.arn
}

output "parquet_lambda_function_arn" {
  value = aws_lambda_function.parquet_processor_function.arn
}
