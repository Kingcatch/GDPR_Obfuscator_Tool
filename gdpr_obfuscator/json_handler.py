def json_handler(bucket, file_name):
    print(f"Json Handler called for file: {file_name}")
    return {'statusCode': 200, 'body': 'Json file routed successfully'}
    