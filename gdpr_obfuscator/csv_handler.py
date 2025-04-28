def csv_handler(bucket, file_name):
    print(f"CSV Handler called for file: {file_name}")
    return {'statusCode': 200, 'body': 'CSV routed successfully'}
