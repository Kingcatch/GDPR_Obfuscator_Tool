import boto3
import json
import pandas as pd
import io

s3_client = boto3.client('s3')



def json_processor(bucket, file_name, pii_fields):
    print(f"Json Handler called for file: {file_name} in bucket: {bucket}")
    
    response = s3_client.get_object(Bucket=bucket, Key=file_name)
    content = response['Body'].read().decode('utf-8')
    records = json.loads(content)
    
    df =pd.DataFrame(records)
    
    for field in pii_fields:
        if field in df.columns:
            df[field] = df[field].apply(lambda x: '*' * len(str(x)) if pd.notna(x) else x)

    obfuscated_data = df.to_dict(orient='records')
    obfuscated_json = json.dumps(obfuscated_data, indent=2).encode('utf-8')

    output_key = f"obfuscated/{file_name.split('/')[-1]}"
    s3_client.put_object(Bucket=bucket, Key=output_key, Body=obfuscated_json)

    return {'statusCode': 200, 'body': f'JSON file obfuscated and saved to {output_key}'}
            


def lambda_handler(event, context):
    bucket = event.get('bucket')
    file_name = event.get('file_name')
    pii_fields = event.get('pii_fields', [])
    return json_processor(bucket, file_name, pii_fields)
    