
resource "aws_cloudwatch_log_group" "dispatcher_log_group" {
  name = "/aws/lambda/${aws_lambda_function.dispatcher_function.function_name}"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "csv_processor_log_group" {
  name = "/aws/lambda/${aws_lambda_function.csv_processor_function.function_name}"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "json_processor_log_group" {
  name = "/aws/lambda/${aws_lambda_function.json_processor_function.function_name}"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "parquet_processor_log_group" {
  name = "/aws/lambda/${aws_lambda_function.parquet_processor_function.function_name}"
  retention_in_days = 7
}


resource "aws_iam_role_policy_attachment" "dispatcher_cloudwatch_policy_attachment" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

resource "aws_iam_role_policy_attachment" "csv_processor_cloudwatch_policy_attachment" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

resource "aws_iam_role_policy_attachment" "json_processor_cloudwatch_policy_attachment" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

resource "aws_iam_role_policy_attachment" "parquet_processor_cloudwatch_policy_attachment" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}
