def parquet_handler(bucket, file_name):
    print(f"Parquet Handler called for file: {file_name}")
    return {'statusCode': 200, 'body': 'Parquet routed successfully'}