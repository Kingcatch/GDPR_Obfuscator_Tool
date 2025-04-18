import csv, io, json
import boto3, logging
import csv_handler, json_handler, parquet_handler

logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3 = boto3.client('s3')

def lambda_handler(event, context):
    """
    Dispatcher Lambda function triggered by an S3 upload event.
    It determines the file type (e.g. CSV, JSON, Parquet) and routes 
    the event to the appropriate processing Lambda function.

    Args:
        event (dict): Event data from S3 trigger.
        context (LambdaContext): Runtime information provided by AWS Lambda.
    Returns:
        dict: Response with status code and message.
    """
    try:
        logger.info("Received event: %s", event)
        # get bucket and file name
        
        bucket = event['Records'][0]['s3']['bucket']['name']
        file_name = event['Records'][0]['s3']['object']['key']
        logger.info("Bucket: %s, File Name: %s", bucket, file_name)
        
        # get file extension
        file_extension = file_name.split('.')[-1].lower()
        logger.info("File Extension: %s", file_extension)
        
        # determine file type and route to appropriate function
        if file_extension == 'csv':
            logger.info("Routing to CSV processing function")
            return csv_handler(bucket, file_name)
        elif file_extension == 'json':
            logger.info("Routing to JSON processing function")
            return json_handler(bucket, file_name)
        elif file_extension == 'parquet':
            logger.info("Routing to Parquet processing function")
            return parquet_handler(bucket, file_name)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    except Exception as e:
        logger.error("Error processing file: %s", e)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing file',
                'error': str(e)
            })
        }
        