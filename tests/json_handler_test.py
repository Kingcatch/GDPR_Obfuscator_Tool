import io
import pytest
import json
from unittest.mock import patch, MagicMock
from gdpr_obfuscator import json_handler
from botocore.exceptions import ClientError


# ==========================
# Tests for json_processor
# ==========================

@patch("gdpr_obfuscator.json_handler.s3")
def test_json_processor_valid(mock_s3):
    test_data = [{"name": "John", "email": "john@example.com", "age": 30}]
    mock_body = io.BytesIO(json.dumps(test_data).encode("utf-8"))
    mock_s3.get_object.return_value = {"Body": mock_body}

    mock_s3.put_object = MagicMock()

    response = json_handler.json_processor(
        bucket="obfuscator-tool-bucket",
        file_name="sample.json",
        pii_fields=["name", "email"]
    )

    assert response["statusCode"] == 200
    assert "obfuscated" in response["body"]


@patch("gdpr_obfuscator.json_handler.s3")
def test_json_processor_missing_pii_fields(mock_s3):
    test_data = [{"name": "John", "age": 30}]
    mock_body = io.BytesIO(json.dumps(test_data).encode("utf-8"))
    mock_s3.get_object.return_value = {"Body": mock_body}

    response = json_handler.json_processor(
        bucket="obfuscator-tool-bucket",
        file_name="missing_fields.json",
        pii_fields=["email"]
    )

    assert response["statusCode"] == 200
    assert "obfuscated" in response["body"]


@patch("gdpr_obfuscator.json_handler.s3")
def test_json_processor_empty_file(mock_s3):
    mock_body = io.BytesIO(b"")
    mock_s3.get_object.return_value = {"Body": mock_body}

    with pytest.raises(ValueError, match="JSON file .* is empty or unreadable."):
        json_handler.json_processor(
            bucket="obfuscator-tool-bucket",
            file_name="empty.json",
            pii_fields=["name"]
        )


@patch("gdpr_obfuscator.json_handler.s3")
def test_json_processor_invalid_json(mock_s3):
    mock_body = io.BytesIO(b"{not valid json}")
    mock_s3.get_object.return_value = {"Body": mock_body}

    with pytest.raises(ValueError, match="JSON file .* is not a valid JSON format."):
        json_handler.json_processor(
            bucket="obfuscator-tool-bucket",
            file_name="bad.json",
            pii_fields=["name"]
        )


@patch("gdpr_obfuscator.json_handler.s3")
def test_json_processor_not_list_of_dicts(mock_s3):
    mock_body = io.BytesIO(json.dumps({"name": "John"}).encode("utf-8"))
    mock_s3.get_object.return_value = {"Body": mock_body}

    with pytest.raises(ValueError, match="must contain a list of JSON objects"):
        json_handler.json_processor(
            bucket="obfuscator-tool-bucket",
            file_name="single_object.json",
            pii_fields=["name"]
        )


@patch("gdpr_obfuscator.json_handler.s3")
def test_json_processor_s3_error(mock_s3):
    mock_s3.get_object.side_effect = ClientError(
        {"Error": {"Code": "NoSuchKey", "Message": "Not found"}}, "GetObject"
    )

    with pytest.raises(ClientError):
        json_handler.json_processor(
            bucket="obfuscator-tool-bucket",
            file_name="missing.json",
            pii_fields=["name"]
        )


# ==========================
# Tests for lambda_handler
# ==========================

@patch("gdpr_obfuscator.json_handler.json_processor")
def test_lambda_handler_success(mock_processor):
    mock_processor.return_value = {
        "statusCode": 200,
        "body": "JSON processed and uploaded to obfuscated-files-bucket"
    }

    event = {
        "Records": [{
            "s3": {
                "bucket": {"name": "obfuscator-tool-bucket"},
                "object": {"key": "test_file.json"}
            }
        }],
        "pii_fields": ["name", "email"]
    }

    result = json_handler.lambda_handler(event, None)

    mock_processor.assert_called_once_with(
        bucket="obfuscator-tool-bucket",
        file_name="test_file.json",
        pii_fields=["name", "email"]
    )
    assert result["statusCode"] == 200


@patch("gdpr_obfuscator.json_handler.json_processor")
def test_lambda_handler_defaults_pii_fields(mock_processor):
    mock_processor.return_value = {"statusCode": 200, "body": "OK"}

    event = {
        "Records": [{
            "s3": {
                "bucket": {"name": "obfuscator-tool-bucket"},
                "object": {"key": "test_file.json"}
            }
        }]
    }

    result = json_handler.lambda_handler(event, None)

    mock_processor.assert_called_once_with(
        bucket="obfuscator-tool-bucket",
        file_name="test_file.json",
        pii_fields=[]
    )
    assert result["statusCode"] == 200


@patch("gdpr_obfuscator.json_handler.json_processor")
def test_lambda_handler_exception(mock_processor):
    mock_processor.side_effect = Exception("Processing error")

    event = {
        "Records": [{
            "s3": {
                "bucket": {"name": "obfuscator-tool-bucket"},
                "object": {"key": "test_file.json"}
            }
        }],
        "pii_fields": ["name"]
    }

    with pytest.raises(Exception, match="Processing error"):
        json_handler.lambda_handler(event, None)


def test_lambda_handler_invalid_event_structure():
    bad_event = {}  # Missing 'Records'

    with pytest.raises(KeyError):
        json_handler.lambda_handler(bad_event, None)
