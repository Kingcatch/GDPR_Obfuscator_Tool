import io
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from gdpr_obfuscator import parquet_handler
from botocore.exceptions import ClientError


# ==========================
# Tests for parquet_processor
# ==========================

@patch("gdpr_obfuscator.parquet_handler.s3")
def test_parquet_processor_valid(mock_s3):
    # Sample Parquet content
    df = pd.DataFrame({"name": ["John"], "email": ["john@example.com"], "age": [30]})
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)

    mock_s3.get_object.return_value = {"Body": buffer}
    mock_s3.put_object = MagicMock()

    response = parquet_handler.parquet_processor(
        bucket="obfuscator-tool-bucket",
        file_name="sample.parquet",
        pii_fields=["name", "email"]
    )

    assert response["statusCode"] == 200
    assert "processed and uploaded" in response["body"]


@patch("gdpr_obfuscator.parquet_handler.s3")
def test_parquet_processor_missing_pii_fields(mock_s3):
    df = pd.DataFrame({"name": ["Alice"], "age": [25]})
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)

    mock_s3.get_object.return_value = {"Body": buffer}
    mock_s3.put_object = MagicMock()

    response = parquet_handler.parquet_processor(
        bucket="obfuscator-tool-bucket",
        file_name="missing_fields.parquet",
        pii_fields=["email"]
    )

    assert response["statusCode"] == 200
    assert "processed and uploaded" in response["body"]


@patch("gdpr_obfuscator.parquet_handler.s3")
def test_parquet_processor_s3_error(mock_s3):
    mock_s3.get_object.side_effect = ClientError(
        {"Error": {"Code": "NoSuchKey", "Message": "Not found"}}, "GetObject"
    )

    with pytest.raises(ClientError):
        parquet_handler.parquet_processor(
            bucket="obfuscator-tool-bucket",
            file_name="nonexistent.parquet",
            pii_fields=["name"]
        )


@patch("gdpr_obfuscator.parquet_handler.s3")
def test_parquet_processor_invalid_file(mock_s3):
    mock_s3.get_object.return_value = {"Body": io.BytesIO(b"Not a parquet file")}

    with pytest.raises(RuntimeError, match="Error processing Parquet file"):
        parquet_handler.parquet_processor(
            bucket="obfuscator-tool-bucket",
            file_name="invalid.parquet",
            pii_fields=["name"]
        )


# ==========================
# Tests for lambda_handler
# ==========================

@patch("gdpr_obfuscator.parquet_handler.parquet_processor")
def test_lambda_handler_success(mock_processor):
    mock_processor.return_value = {
        "statusCode": 200,
        "body": "Parquet processed and uploaded"
    }

    event = {
        "Records": [{
            "s3": {
                "bucket": {"name": "obfuscator-tool-bucket"},
                "object": {"key": "test_file.parquet"}
            }
        }],
        "pii_fields": ["name", "email"]
    }

    result = parquet_handler.lambda_handler(event, None)

    mock_processor.assert_called_once_with(
        bucket="obfuscator-tool-bucket",
        file_name="test_file.parquet",
        pii_fields=["name", "email"]
    )

    assert result["statusCode"] == 200


@patch("gdpr_obfuscator.parquet_handler.parquet_processor")
def test_lambda_handler_default_pii_fields(mock_processor):
    mock_processor.return_value = {"statusCode": 200, "body": "OK"}

    event = {
        "Records": [{
            "s3": {
                "bucket": {"name": "obfuscator-tool-bucket"},
                "object": {"key": "test_file.parquet"}
            }
        }]
    }

    result = parquet_handler.lambda_handler(event, None)

    mock_processor.assert_called_once_with(
        bucket="obfuscator-tool-bucket",
        file_name="test_file.parquet",
        pii_fields=[]
    )
    assert result["statusCode"] == 200


def test_lambda_handler_invalid_event_structure():
    bad_event = {}  # Missing 'Records'

    with pytest.raises(KeyError, match="Invalid event structure"):
        parquet_handler.lambda_handler(bad_event, None)



