import json
import io
import pytest
from unittest.mock import patch
from gdpr_obfuscator import dispatcher

import sys
print(sys.path)


# Mocking the invoke function for the Lambda client
@patch('dispatcher.lambda_client.invoke')
def test_lambda_handler_csv(mock_invoke):
    mock_invoke.return_value = {'StatusCode': 202}

    event = {
        "Records": [{
            "s3": {
                "bucket": {"name": "test-bucket"},
                "object": {"key": "file.csv"}
            }
        }]
    }

    # Test for a CSV file
    response = dispatcher.lambda_handler(event, None)  # Corrected reference to lambda_handler

    # Ensure that invoke is called with the correct parameters
    mock_invoke.assert_called_once_with(
        FunctionName='csv_processor',
        InvocationType='Event',
        Payload=json.dumps({'bucket': 'test-bucket', 'file_name': 'file.csv'})
    )
    assert response['statusCode'] == 202
    assert "Invocation of csv_processor accepted" in response['body']


@patch('dispatcher.lambda_client.invoke')
def test_lambda_handler_json(mock_invoke):
    mock_invoke.return_value = {'StatusCode': 202}

    event = {
        "Records": [{
            "s3": {
                "bucket": {"name": "test-bucket"},
                "object": {"key": "file.json"}
            }
        }]
    }

    # Test for a JSON file
    response = dispatcher.lambda_handler(event, None)  # Corrected reference to lambda_handler

    # Ensure that invoke is called with the correct parameters
    mock_invoke.assert_called_once_with(
        FunctionName='json_processor',
        InvocationType='Event',
        Payload=json.dumps({'bucket': 'test-bucket', 'file_name': 'file.json'})
    )
    assert response['statusCode'] == 202
    assert "Invocation of json_processor accepted" in response['body']


@patch('dispatcher.lambda_client.invoke')
def test_lambda_handler_parquet(mock_invoke):
    mock_invoke.return_value = {'StatusCode': 202}

    event = {
        "Records": [{
            "s3": {
                "bucket": {"name": "test-bucket"},
                "object": {"key": "file.parquet"}
            }
        }]
    }

    # Test for a Parquet file
    response = dispatcher.lambda_handler(event, None)  # Corrected reference to lambda_handler

    # Ensure that invoke is called with the correct parameters
    mock_invoke.assert_called_once_with(
        FunctionName='parquet_processor',
        InvocationType='Event',
        Payload=json.dumps({'bucket': 'test-bucket', 'file_name': 'file.parquet'})
    )
    assert response['statusCode'] == 202
    assert "Invocation of parquet_processor accepted" in response['body']


@patch('dispatcher.lambda_client.invoke')
def test_lambda_handler_unsupported_file_type(mock_invoke):
    mock_invoke.return_value = {'StatusCode': 202}

    event = {
        "Records": [{
            "s3": {
                "bucket": {"name": "test-bucket"},
                "object": {"key": "file.txt"}
            }
        }]
    }

    # Test for unsupported file type
    response = dispatcher.lambda_handler(event, None)  # Corrected reference to lambda_handler

    # Ensure the correct response for unsupported file types
    assert response['statusCode'] == 400
    assert "Unsupported file type" in response['body']


def test_lambda_handler_missing_records():
    event = {}  # Missing 'Records' key

    # Test for invalid event structure (missing 'Records')
    response = dispatcher.lambda_handler(event, None)  # Corrected reference to lambda_handler

    assert response['statusCode'] == 500
    assert "Error processing file" in response['body']


@patch('dispatcher.lambda_client.invoke')
def test_lambda_handler_invocation_failure(mock_invoke):
    # Simulate an invocation failure
    mock_invoke.side_effect = Exception("Lambda invocation failed")

    event = {
        "Records": [{
            "s3": {
                "bucket": {"name": "test-bucket"},
                "object": {"key": "file.csv"}
            }
        }]
    }

    # Test for invocation failure handling
    response = dispatcher.lambda_handler(event, None)  # Corrected reference to lambda_handler

    assert response['statusCode'] == 500
    assert "Error invoking Lambda function" in response['body']
