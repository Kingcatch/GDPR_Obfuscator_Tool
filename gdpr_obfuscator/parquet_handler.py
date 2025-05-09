import io
import boto3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from botocore.exceptions import ClientError

# S3 client
s3 = boto3.client("s3")

# Output bucket
OUTPUT_BUCKET = "obfuscated-files-bucket"


def parquet_processor(bucket, file_name, pii_fields):
    print(f"Parquet Processor invoked for file: {file_name} in bucket: {bucket}")

    try:
        response = s3.get_object(Bucket=bucket, Key=file_name)
        file_stream = io.BytesIO(response["Body"].read())
        df = pd.read_parquet(file_stream)

        for field in pii_fields:
            if field in df.columns:
                df[field] = df[field].apply(lambda x: "*" * len(str(x)) if pd.notna(x) else x)

        # Convert DataFrame to Parquet
        output_stream = io.BytesIO()
        table = pa.Table.from_pandas(df)
        pq.write_table(table, output_stream)
        output_stream.seek(0)

        output_key = f"obfuscated/{file_name.split('/')[-1]}"
        s3.put_object(Bucket=OUTPUT_BUCKET, Key=output_key, Body=output_stream.getvalue())

        return {
            "statusCode": 200,
            "body": f"Parquet file processed and uploaded to {OUTPUT_BUCKET}/{output_key}",
        }

    except ClientError as e:
        raise e

    except Exception as e:
        raise RuntimeError(f"Error processing Parquet file: {str(e)}")


def lambda_handler(event, context):
    try:
        # Ensure that 'Records' is in the event and is correctly structured
        records = event.get("Records", [])
        if not records:
            raise KeyError("Invalid event structure: 'Records' key is missing.")
        
        # Extract bucket and file_name from event
        bucket = records[0]["s3"]["bucket"]["name"]
        file_name = records[0]["s3"]["object"]["key"]
        pii_fields = event.get("pii_fields", [])
        
        # Process the file
        return parquet_processor(bucket=bucket, file_name=file_name, pii_fields=pii_fields)
    
    except KeyError as e:
        # Python will automatically raise the KeyError if the event structure is invalid
        raise e


