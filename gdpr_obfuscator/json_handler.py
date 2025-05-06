import boto3
import json
import pandas as pd

s3 = boto3.client('s3')


def json_processor(bucket, file_name, pii_fields):
    print(f"JSON Handler called for file: {file_name} in bucket: {bucket}")
    
    obj = s3.get_object(Bucket=bucket, Key=file_name)
    content = obj['Body'].read().decode('utf-8')
    records = json.loads(content)
    
    df = pd.DataFrame(records)
    
    for field in pii_fields:
        if field in df.columns:
            df[field] = df[field].apply(lambda x: '*' * len(str(x)) if pd.notna(x) else x)
    
    obfuscated_data = df.to_dict(orient='records')
    obfuscated_json = json.dumps(obfuscated_data, indent=2).encode('utf-8')
    
    obfuscated_file_name = f"obfuscated_{file_name.split('/')[-1]}"
    obfuscated_bucket = 'obfuscated-files-bucket'
    s3.put_object(Bucket=obfuscated_bucket, Key=obfuscated_file_name, Body=obfuscated_json)
    
    return {'statusCode': 200, 'body': 'JSON processed and uploaded to obfuscated-files-bucket'}


def lambda_handler(event, context):
    s3_uri = event.get('file_to_obfuscate')
    pii_fields = event.get('pii_fields', [])
    
    no_prefix = s3_uri.replace('s3://', '')
    parts = no_prefix.split('/', 1)
    bucket = parts[0]
    file_name = parts[1] if len(parts) > 1 else ''
    
    return json_processor(bucket, file_name, pii_fields)
