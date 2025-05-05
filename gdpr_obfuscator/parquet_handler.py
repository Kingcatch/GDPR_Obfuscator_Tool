import pyarrow.parquet as pq
import boto3
import io
import pyarrow as pa
import pandas as pd

s3_client = boto3.client('s3')

def parquet_processor(bucket, file_name, pii_fields):
    print(f"Parquet Handler called for file: {file_name} in bucket: {bucket}")
    
    response = s3_client.get_object(Bucket=bucket, Key=file_name)
    file_stream = io.BytesIO(response['Body'].read())
    df = pd.read_parquet(file_stream)
    
    for field in pii_fields:
        if field in df.columns:
            df[field] = df[field].apply(lambda x: '*' * len(str(x)) if pd.notna(x) else x)
    
    # Save back as Parquet and upload to S3
    output_stream = io.BytesIO()
    table = pa.Table.from_pandas(df)
    pq.write_table(table, output_stream)
    output_stream.seek(0)

    output_key = f"obfuscated/{file_name.split('/')[-1]}"
    s3_client.put_object(Bucket=bucket, Key=output_key, Body=output_stream.getvalue())

    return {'statusCode': 200, 'body': f'Parquet file obfuscated and saved to {output_key}'}
    

def lambda_handler(event, context):
    bucket = event.get('bucket')
    file_name = event.get('file_name')
    pii_fields = event.get('pii_fields', [])

    return parquet_processor(bucket, file_name)