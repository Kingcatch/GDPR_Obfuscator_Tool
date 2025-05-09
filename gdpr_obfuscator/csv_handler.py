import boto3
import pandas as pd
from io import StringIO
from botocore.exceptions import ClientError

s3 = boto3.client('s3')

def csv_processor(bucket, file_name, pii_fields):
    print(f"CSV Handler called for file: {file_name} in bucket: {bucket}")

 
    try:
        obj = s3.get_object(Bucket=bucket, Key=file_name)
    except ClientError as e:
        raise e

    csv_data = obj['Body'].read().decode('utf-8')

    # Check if the data is all in one line
    if "\n" not in csv_data:
        raise ValueError(f"CSV file seems to have no line breaks. Please ensure the file is properly formatted.")

    df = pd.read_csv(StringIO(csv_data))
    
    if len(df.columns) == 1:
        raise ValueError(f"CSV file {file_name} is malformed — it appears to have all data in a single column.")

    for field in pii_fields:
        if field in df.columns:
            df[field] = df[field].astype(str).apply(lambda x: "*" * len(x))


    obfuscated_csv = df.to_csv(index=False)
    obfuscated_file_name = f"obfuscated_{file_name}"
    obfuscated_bucket = 'obfuscated-files-bucket'

    s3.put_object(Bucket=obfuscated_bucket, Key=obfuscated_file_name, Body=obfuscated_csv)

    return {'statusCode': 200, 'body': 'CSV processed and uploaded to obfuscated-files-bucket'}

def lambda_handler(event, context):
    pii_fields = event.get('pii_fields', [])
    print("PII Fields passed:", pii_fields)

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


    return csv_processor(bucket=bucket, file_name=file_name, pii_fields=pii_fields)
