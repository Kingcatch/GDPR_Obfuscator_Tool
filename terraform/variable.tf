variable "region" {
  description = "The AWS region to deploy resources"
  default     = "eu-west-2"
}

variable "input_bucket_name" {
  description = "S3 bucket for input files"
  default     = "obfuscator-tool--bucket"
}

variable "output_bucket_name" {
  description = "S3 bucket for obfuscated files"
  default     = "obfuscated-files-bucket"
}
