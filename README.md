GDPR Obfuscator Tool

Overview
The GDPR Obfuscator is a Python library designed to process data files in CSV, JSON, and Parquet formats, obfuscating personally identifiable information (PII) fields to comply with GDPR regulations. The tool can be deployed in AWS Lambda and works by reading files stored in S3 buckets, obfuscating the specified PII fields, and outputting the processed file back to an S3  bucket.

Features:
- Currently supports CSV and JSON files.
- Obfuscates PII fields (e.g names, email addresses) in the input data.
- Integration with AWS Lambda for scalable, serverless execution.
- Logs progress and errors to AWS CloudWatch.


Requirements:

- Python 3.11.1
- boto3 (AWS SDK for Python)
- pyarrow (for Parquet support)
- pandas (for CSV/JSON data processing)
- AWS Lambda (for deployment)
- AWS S3 (for file storage)
- CloudWatch(for logging and alerts)

**Setup Instructions**

1. Install Dependencies
Clone the repository and install the required dependencies using the requirements.txt file:
pip install -r requirements.txt
Alternatively, running the follwoing MakeFile commands will set up the environment and install dependencies locally for you:
 - make create-environment
 - make dev-setup

2. AWS Setup (Running Terraform should implement this process also):
Create S3 Buckets:
- Create two S3 buckets: one for the input files and another for storing the obfuscated output.

IAM Role Setup:
- Create an IAM role with permissions to read and write to the S3 buckets.
- The role should also allow logging to CloudWatch and sending alerts through SNS.

Configure AWS Lambda:
- Deploy the tool as an AWS Lambda function.
- Ensure that the Lambda function has access to the S3 buckets, CloudWatch, and SNS.


**How to Use the Tool**

Project Structure
The tool consists of the following main scripts:

dispatcher.py: The main entry point that coordinates the invocation and processing of the data. It routes requests to the appropriate handler based on the file format (CSV, JSON, Parquet).

csv_handler.py: Handles processing and obfuscation of CSV files.

json_handler.py: Handles processing and obfuscation of JSON files.

parquet_handler.py: Handles processing and obfuscation of Parquet files.

1. JSON Input Example
The tool is invoked with a JSON string containing:

file_to_obfuscate: The S3 location of the file to process (e.g., s3://my-ingestion-bucket/data/file1.csv).

pii_fields: A list of PII field names to be obfuscated (e.g., name, email_address).

Example Input:
json
Copy
Edit
{
  "file_to_obfuscate": "s3://my-ingestion-bucket/data/file1.csv",
  "pii_fields": ["name", "email_address"]
}
2. Supported File Formats
CSV: The tool reads CSV files, processes the data, and obfuscates the specified PII fields using the csv_handler.py.

JSON: The tool supports JSON format and obfuscates PII fields in JSON objects using the json_handler.py.



Example Input Data (CSV):
csv
Copy
Edit
student_id,name,course,cohort,graduation_date,email_address
1234,John Smith,Software,2024-03-31,j.smith@email.com
5678,Jane Doe,Data Science,2024-06-15,jane.doe@email.com
Example Output Data (Obfuscated):
csv
Copy
Edit
student_id,name,course,cohort,graduation_date,email_address
1234,***,Software,2024-03-31,***
5678,***,Data Science,2024-06-15,***


3. How It Works
The dispatcher.py script reads the input JSON, extracting the S3 file location and the PII fields to obfuscate.

Based on the file format (CSV, JSON, or Parquet), the dispatcher routes the request to the appropriate handler (csv_handler.py, json_handler.py, or parquet_handler.py).

The respective handler processes the file, obfuscating the specified PII fields.

The obfuscated file is returned as a byte-stream and uploaded to the designated output S3 bucket.

4. Example Workflow
Trigger: An AWS service (like EventBridge, Step Functions, or Lambda) triggers the tool with a JSON payload.

Obfuscation: The tool reads the file from S3, obfuscates the specified fields, and generates the obfuscated file.

Storage: The obfuscated file is uploaded back to an S3 bucket.

Example Output (JSON Response):
json
Copy
Edit
{
  "status": "success",
  "message": "File obfuscated and uploaded to S3 successfully.",
  "output_file_location": "s3://my-output-bucket/obfuscated_file.csv"
}
5. Logging and Alerts
CloudWatch Logs: All operations are logged to CloudWatch, providing insight into the execution of the tool.

Testing the Tool Locally
You can test the tool locally before deploying it to AWS Lambda by invoking the handlers directly.

1. Prepare Sample Files
Place a sample CSV, JSON, or Parquet file in the data folder.

2. Run the Dispatcher Script
Use the dispatcher.py script to trigger the obfuscation process locally.

Example Command:

python dispatcher.py --input_file s3://my-ingestion-bucket/data/file1.csv --pii_fields name,email_address

3. Check Output
The obfuscated file will be printed or saved locally, depending on your script configuration.

Non-functional Utils:

- File Size: The tool can process files up to 1MB in size with a processing time of less than 1 minute.
- Security: The code ensures that no sensitive data is exposed during processing. 
- Code Quality: The code is designed to be PEP-8 compliant, well-documented, and includes unit tests.
- Deployment: The tool is designed to be deployed as an AWS Lambda function.

**Extensions**
Future extensions for the tool may include:

- Support for Additional File Formats: Adding support for additional file formats such as parquet, XML or Excel.

- Additional testing for error handling within the main dispatcher handler

- Dynamic implementation, including updating the specified pii_fields for obfuscation to match file contents.

- Implementation of a CLI Wrapper to invoke the function directly from the command line

- Advanced Obfuscation Techniques: Implementing more complex obfuscation techniques like tokenization or data masking.
