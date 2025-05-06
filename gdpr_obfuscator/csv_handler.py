import boto3
import pandas as pd
from io import StringIO

s3 = boto3.client('s3')


def csv_processor(bucket, file_name, pii_fields):
    print(f"CSV Handler called for file: {file_name} in bucket: {bucket}")
    
    obj = s3.get_object(Bucket=bucket, Key=file_name)
    csv_data = obj['Body'].read().decode('utf-8')
    df = pd.read_csv(StringIO(csv_data))
    
    for field in pii_fields:
        if field in df.columns:
            df[field] = '*' * df[field].astype(str).str.len()
            
    obfuscated_csv = df.to_csv(index=False)
    obfuscated_file_name = f"obfuscated_{file_name}"
    
    # Upload the obfuscated CSV to the new 'obfuscated-files-bucket'
    obfuscated_bucket = 'obfuscated-files-bucket'
    s3.put_object(Bucket=obfuscated_bucket, Key=obfuscated_file_name, Body=obfuscated_csv)
    
    return {'statusCode': 200, 'body': 'CSV processed and uploaded to obfuscated-files-bucket'}

def lambda_handler(event, context):
    # Retrieve S3 URI and PII fields from the event
    s3_uri = event.get('file_to_obfuscate')
    pii_fields = event.get('pii_fields', [])
    
    no_prefix = s3_uri.replace('s3://', '')
    parts = no_prefix.split('/', 1)
    bucket = parts[0]
    file_name = parts[1] if len(parts) > 1 else ''
    
    # Call the CSV processor to obfuscate the file and upload it to the new bucket
    return csv_processor(bucket, file_name, pii_fields)
