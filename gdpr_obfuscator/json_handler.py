import boto3
import json
import pandas as pd
from botocore.exceptions import ClientError

s3 = boto3.client('s3')


def json_processor(bucket, file_name, pii_fields):
    print(f"JSON Handler called for file: {file_name} in bucket: {bucket}")

    # Retrieve file from S3
    try:
        obj = s3.get_object(Bucket=bucket, Key=file_name)
    except ClientError as e:
        raise e

    content = obj['Body'].read().decode('utf-8').strip()

    # Validate content presence
    if not content:
        raise ValueError(f"JSON file {file_name} is empty or unreadable.")

    try:
        records = json.loads(content)
    except json.JSONDecodeError:
        raise ValueError(f"JSON file {file_name} is not a valid JSON format.")

    # Ensure data is a list of dicts
    if not isinstance(records, list) or not all(isinstance(record, dict) for record in records):
        raise ValueError(f"JSON file {file_name} must contain a list of JSON objects.")

    df = pd.DataFrame(records)

    # Obfuscate PII fields
    for field in pii_fields:
        if field in df.columns:
            df[field] = df[field].apply(lambda x: '*' * len(str(x)) if pd.notna(x) else x)

    # Convert back to JSON
    obfuscated_data = df.to_dict(orient='records')
    obfuscated_json = json.dumps(obfuscated_data, indent=2).encode('utf-8')

    obfuscated_file_name = f"obfuscated_{file_name.split('/')[-1]}"
    obfuscated_bucket = 'obfuscated-files-bucket'

    s3.put_object(Bucket=obfuscated_bucket, Key=obfuscated_file_name, Body=obfuscated_json)

    return {'statusCode': 200, 'body': 'JSON processed and uploaded to obfuscated-files-bucket'}


def lambda_handler(event, context):
    pii_fields = event.get('pii_fields', [])
    print("PII Fields passed:", pii_fields)

    # Parse S3 details
    if 'file_to_obfuscate' in event:
        s3_uri = event['file_to_obfuscate']
        no_prefix = s3_uri.replace('s3://', '')
        bucket, file_name = no_prefix.split('/', 1)
    elif 'Records' in event:
        try:
            record = event['Records'][0]
            bucket = record['s3']['bucket']['name']
            file_name = record['s3']['object']['key']
        except (KeyError, IndexError):
            raise KeyError("Malformed S3 event structure: missing bucket or key info")
    else:
        raise KeyError("Missing required S3 input: 'file_to_obfuscate' or 'Records'")

    return json_processor(bucket=bucket, file_name=file_name, pii_fields=pii_fields)
