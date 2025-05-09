import csv, io, json
import boto3, logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3 = boto3.client('s3')
lambda_client = boto3.client('lambda')

def invoke_main_lambda_handler(function_name, bucket, file_name):
    """
    Invokes the appropriate Lambda function to process the uploaded file.

Args:
    function_name (str): The name of the target Lambda function to invoke.
    bucket (str): The name of the S3 bucket containing the uploaded file.
    file_name (str): The key (path/filename) of the uploaded object in the bucket.

Returns:
    dict: The response from the invoked Lambda function (invocation metadata, not the function's execution result).
    """
    payload = {
        'bucket': bucket,
        'file_name': file_name
    }
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='Event',
            Payload=json.dumps(payload),
        )
        logger.info(f"invoked {function_name} lambda successfully")
        return {
            'statusCode': 202,
            'body': json.dumps(f"Invocation of {function_name} accepted")
        }
    except Exception as e:
        logger.error(f"Error invoking Lambda function {function_name}: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f"Error invoking Lambda function {function_name}",
                'error': str(e)
            })
        }

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
    
        
        bucket = event['Records'][0]['s3']['bucket']['name']
        file_name = event['Records'][0]['s3']['object']['key']
        logger.info("Bucket: %s, File Name: %s", bucket, file_name)
        
        file_extension = file_name.split('.')[-1].lower()
        logger.info("File Extension: %s", file_extension)
      
        
   
        file_extension = file_name.split('.')[-1].lower()
        logger.info("File Extension: %s", file_extension)
        

        if file_extension == 'csv':
            logger.info("Routing to CSV processing function")
            return invoke_main_lambda_handler('csv_processor', bucket, file_name)
        elif file_extension == 'json':
            logger.info("Routing to JSON processing function")
            return invoke_main_lambda_handler('json_processor', bucket, file_name)
        elif file_extension == 'parquet':
            logger.info("Routing to Parquet processing function")
            return invoke_main_lambda_handler('parquet_processor', bucket, file_name)
        else:
            logger.warning(f"Unsupported file type: {file_extension}")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'Unsupported file type',
                    'file_extension': file_extension
                })
            }
    except Exception as e:
        logger.error("Error processing file: %s", e)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing file',
                'error': str(e)
            })
        }
        