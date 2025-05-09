import io
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from gdpr_obfuscator import csv_handler
from botocore.exceptions import ClientError


# ==========================
# Tests for csv_processor
# ==========================

@patch("gdpr_obfuscator.csv_handler.s3")
def test_csv_processor_valid(mock_s3):
    mock_body = io.BytesIO(b"name,email,age\nJohn,john@example.com,30")
    mock_s3.get_object.return_value = {"Body": mock_body}

    mock_upload = MagicMock()
    mock_s3.put_object = mock_upload

    response = csv_handler.csv_processor(
        bucket="obfuscator-tool-bucket",
        file_name="sample.csv",
        pii_fields=["name", "email"]
    )

    assert response["statusCode"] == 200
    assert "obfuscated" in response["body"]


@patch("gdpr_obfuscator.csv_handler.s3")
def test_csv_processor_missing_pii_fields(mock_s3):
    mock_body = io.BytesIO(b"name,age\nJohn,30")
    mock_s3.get_object.return_value = {"Body": mock_body}

    response = csv_handler.csv_processor(
        bucket="obfuscator-tool-bucket",
        file_name="missing_fields.csv",
        pii_fields=["email"]
    )

    assert response["statusCode"] == 200
    assert "obfuscated" in response["body"]


@patch("gdpr_obfuscator.csv_handler.s3")
def test_csv_processor_missing_header(mock_s3):
    mock_body = io.BytesIO(b"")
    mock_s3.get_object.return_value = {"Body": mock_body}

    with pytest.raises(ValueError, match=r"CSV file seems to have no line breaks. Please ensure the file is properly formatted."):
        csv_handler.csv_processor(
            bucket="obfuscator-tool-bucket",
            file_name="empty.csv",
            pii_fields=["name"]
        )


@patch("gdpr_obfuscator.csv_handler.s3")
def test_csv_processor_s3_error(mock_s3):
    mock_s3.get_object.side_effect = ClientError(
        {"Error": {"Code": "NoSuchKey", "Message": "Not found"}}, "GetObject"
    )

    with pytest.raises(ClientError):
        csv_handler.csv_processor(
            bucket="obfuscator-tool-bucket",
            file_name="missing.csv",
            pii_fields=["email"]
        )


# ==========================
# Tests for lambda_handler
# ==========================

@patch("gdpr_obfuscator.csv_handler.csv_processor")
def test_lambda_handler_success(mock_processor):
    mock_processor.return_value = {
        "statusCode": 200,
        "body": "CSV processed and uploaded to obfuscated-files-bucket"
    }

    event = {
        "Records": [{
            "s3": {
                "bucket": {"name": "obfuscator-tool-bucket"},
                "object": {"key": "test_file.csv"}
            }
        }],
        "pii_fields": ["name", "email"]
    }

    result = csv_handler.lambda_handler(event, None)

    mock_processor.assert_called_once_with(
        bucket="obfuscator-tool-bucket",
        file_name="test_file.csv",
        pii_fields=["name", "email"]
    )
    assert result["statusCode"] == 200
    assert result["body"] == "CSV processed and uploaded to obfuscated-files-bucket"


@patch("gdpr_obfuscator.csv_handler.csv_processor")
def test_lambda_handler_defaults_pii_fields(mock_processor):
    mock_processor.return_value = {"statusCode": 200, "body": "OK"}

    event = {
        "Records": [{
            "s3": {
                "bucket": {"name": "obfuscator-tool-bucket"},
                "object": {"key": "test_file.csv"}
            }
        }]
    }

    result = csv_handler.lambda_handler(event, None)

    mock_processor.assert_called_once_with(
        bucket="obfuscator-tool-bucket",
        file_name="test_file.csv",
        pii_fields=[]
    )
    assert result["statusCode"] == 200


@patch("gdpr_obfuscator.csv_handler.csv_processor")
def test_lambda_handler_exception(mock_processor):
    mock_processor.side_effect = Exception("Processing error")

    event = {
        "Records": [{
            "s3": {
                "bucket": {"name": "obfuscator-tool-bucket"},
                "object": {"key": "test_file.csv"}
            }
        }],
        "pii_fields": ["name"]
    }

    with pytest.raises(Exception, match="Processing error"):
        csv_handler.lambda_handler(event, None)


def test_lambda_handler_invalid_event_structure():
    bad_event = {}  # Missing 'Records'

    with pytest.raises(KeyError):
        csv_handler.lambda_handler(bad_event, None)
