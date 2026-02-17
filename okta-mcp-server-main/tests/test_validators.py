"""Tests for input validation utilities."""

import pytest

from okta_mcp_server.utils.validators import (
    ValidationError,
    sanitize_error,
    validate_email,
    validate_iso_timestamp,
    validate_limit,
    validate_okta_id,
    validate_profile_dict,
    validate_required_string,
)


class TestValidateEmail:
    """Tests for validate_email."""

    def test_valid_email(self):
        valid, err = validate_email("user@example.com")
        assert valid is True
        assert err is None

    def test_valid_email_with_plus(self):
        valid, err = validate_email("user+tag@example.com")
        assert valid is True

    def test_empty_string(self):
        valid, err = validate_email("")
        assert valid is False
        assert "required" in err

    def test_missing_at_sign(self):
        valid, err = validate_email("userexample.com")
        assert valid is False
        assert "Invalid email format" in err

    def test_missing_domain(self):
        valid, err = validate_email("user@")
        assert valid is False

    def test_too_long(self):
        valid, err = validate_email("a" * 250 + "@b.com")
        assert valid is False
        assert "too long" in err

    def test_non_string_type(self):
        valid, err = validate_email(12345)
        assert valid is False
        assert "string" in err


class TestValidateOktaId:
    """Tests for validate_okta_id."""

    def test_valid_id(self):
        valid, err = validate_okta_id("00u1abc123def456")
        assert valid is True
        assert err is None

    def test_valid_id_with_hyphens_underscores(self):
        valid, err = validate_okta_id("abc-def_123")
        assert valid is True

    def test_empty_string(self):
        valid, err = validate_okta_id("")
        assert valid is False
        assert "required" in err

    def test_too_long(self):
        valid, err = validate_okta_id("a" * 101)
        assert valid is False
        assert "too long" in err

    def test_invalid_characters(self):
        valid, err = validate_okta_id("abc@def")
        assert valid is False
        assert "invalid characters" in err

    def test_custom_field_name(self):
        valid, err = validate_okta_id("", field_name="user_id")
        assert "user_id" in err

    def test_non_string_type(self):
        valid, err = validate_okta_id(12345)
        assert valid is False
        assert "string" in err


class TestValidateIsoTimestamp:
    """Tests for validate_iso_timestamp."""

    def test_valid_utc_timestamp(self):
        valid, err = validate_iso_timestamp("2024-01-15T10:30:00Z")
        assert valid is True
        assert err is None

    def test_valid_with_milliseconds(self):
        valid, err = validate_iso_timestamp("2024-01-15T10:30:00.123Z")
        assert valid is True

    def test_valid_with_timezone_offset(self):
        valid, err = validate_iso_timestamp("2024-01-15T10:30:00+05:30")
        assert valid is True

    def test_empty_string_is_optional(self):
        valid, err = validate_iso_timestamp("")
        assert valid is True
        assert err is None

    def test_invalid_format(self):
        valid, err = validate_iso_timestamp("not-a-timestamp")
        assert valid is False
        assert "ISO 8601" in err

    def test_non_string_type(self):
        valid, err = validate_iso_timestamp(12345)
        assert valid is False
        assert "string" in err


class TestValidateLimit:
    """Tests for validate_limit."""

    def test_none_returns_default(self):
        value, warn = validate_limit(None)
        assert value == 20
        assert warn is None

    def test_valid_value(self):
        value, warn = validate_limit(50)
        assert value == 50
        assert warn is None

    def test_below_minimum(self):
        value, warn = validate_limit(5)
        assert value == 20
        assert "below minimum" in warn

    def test_above_maximum(self):
        value, warn = validate_limit(200)
        assert value == 100
        assert "exceeds maximum" in warn

    def test_custom_bounds(self):
        value, warn = validate_limit(5, min_val=1, max_val=10)
        assert value == 5
        assert warn is None

    def test_non_integer_convertible(self):
        value, warn = validate_limit("50")
        assert value == 50

    def test_non_integer_not_convertible(self):
        value, warn = validate_limit("abc")
        assert value == 20
        assert "integer" in warn

    def test_boundary_min(self):
        value, warn = validate_limit(20)
        assert value == 20
        assert warn is None

    def test_boundary_max(self):
        value, warn = validate_limit(100)
        assert value == 100
        assert warn is None


class TestValidateRequiredString:
    """Tests for validate_required_string."""

    def test_valid_string(self):
        valid, err = validate_required_string("hello", "name")
        assert valid is True
        assert err is None

    def test_none_value(self):
        valid, err = validate_required_string(None, "name")
        assert valid is False
        assert "required" in err

    def test_empty_string(self):
        valid, err = validate_required_string("", "name")
        assert valid is False
        assert "empty" in err

    def test_whitespace_only(self):
        valid, err = validate_required_string("   ", "name")
        assert valid is False
        assert "empty" in err

    def test_non_string_type(self):
        valid, err = validate_required_string(123, "name")
        assert valid is False
        assert "string" in err

    def test_field_name_in_error(self):
        valid, err = validate_required_string(None, "email_address")
        assert "email_address" in err


class TestValidateProfileDict:
    """Tests for validate_profile_dict."""

    def test_valid_dict(self):
        valid, err = validate_profile_dict({"firstName": "Test"})
        assert valid is True
        assert err is None

    def test_none_value(self):
        valid, err = validate_profile_dict(None)
        assert valid is False
        assert "required" in err

    def test_non_dict_type(self):
        valid, err = validate_profile_dict("not a dict")
        assert valid is False
        assert "dictionary" in err

    def test_missing_required_fields(self):
        valid, err = validate_profile_dict({"firstName": "Test"}, required_fields=["firstName", "lastName"])
        assert valid is False
        assert "lastName" in err

    def test_all_required_fields_present(self):
        valid, err = validate_profile_dict(
            {"firstName": "Test", "lastName": "User"},
            required_fields=["firstName", "lastName"],
        )
        assert valid is True

    def test_required_field_with_empty_value(self):
        valid, err = validate_profile_dict({"firstName": ""}, required_fields=["firstName"])
        assert valid is False
        assert "firstName" in err

    def test_no_required_fields(self):
        valid, err = validate_profile_dict({})
        assert valid is True


class TestValidationError:
    """Tests for ValidationError exception."""

    def test_attributes(self):
        err = ValidationError("email", "Invalid format")
        assert err.field == "email"
        assert err.message == "Invalid format"

    def test_string_representation(self):
        err = ValidationError("email", "Invalid format")
        assert "email" in str(err)
        assert "Invalid format" in str(err)

    def test_is_exception(self):
        with pytest.raises(ValidationError):
            raise ValidationError("field", "error")


class TestSanitizeError:
    """Tests for sanitize_error."""

    def test_sanitize_string_error(self):
        result = sanitize_error("Something went wrong")
        assert result == "Something went wrong"

    def test_sanitize_exception_error(self):
        result = sanitize_error(ValueError("Invalid value"))
        assert result == "Invalid value"

    def test_strip_okta_url(self):
        error = "Failed to connect to https://myorg.okta.com/api/v1/users"
        result = sanitize_error(error)
        assert "okta.com" not in result
        assert "[OKTA_URL]" in result

    def test_strip_bearer_token(self):
        error = "Authorization failed with Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        result = sanitize_error(error)
        assert "Bearer" not in result or "[BEARER_TOKEN]" in result

    def test_strip_api_key(self):
        error = "API key sk_live_abcdef1234567890abcd was invalid"
        result = sanitize_error(error)
        assert "sk_live" not in result
        assert "[API_KEY]" in result

    def test_truncate_long_error(self):
        long_error = "x" * 600
        result = sanitize_error(long_error)
        assert len(result) <= 500
        assert result.endswith("...")

    def test_no_truncate_short_error(self):
        short_error = "x" * 100
        result = sanitize_error(short_error)
        assert len(result) == 100
        assert not result.endswith("...")

    def test_sanitize_multiple_urls(self):
        error = "Failed at https://org1.okta.com and https://org2.okta.com"
        result = sanitize_error(error)
        assert "okta.com" not in result
        assert result.count("[OKTA_URL]") == 2

    def test_sanitize_mixed_sensitive_data(self):
        error = "Failed at https://myorg.okta.com/api with Bearer token123"
        result = sanitize_error(error)
        assert "okta.com" not in result
        assert "Bearer" not in result or "[BEARER_TOKEN]" in result

    def test_sanitize_exception_with_sensitive_data(self):
        exc = RuntimeError("Auth failed at https://myorg.okta.com")
        result = sanitize_error(exc)
        assert isinstance(result, str)
        assert "okta.com" not in result
        assert "[OKTA_URL]" in result

    def test_empty_string(self):
        result = sanitize_error("")
        assert result == ""

    def test_okta_id_not_stripped(self):
        error = "User 00u1abc123def456 not found"
        result = sanitize_error(error)
        # Okta IDs like 00u... should NOT be stripped (as per requirements)
        assert "00u1abc123def456" in result
