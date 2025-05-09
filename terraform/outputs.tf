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

