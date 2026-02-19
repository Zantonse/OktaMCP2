# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Input validation utilities for Okta MCP Server tools."""

import re
from datetime import datetime
from typing import Optional, Tuple, Union

# Regex pattern for validating email addresses
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

# Regex pattern for validating Okta IDs (alphanumeric with optional hyphens/underscores)
OKTA_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")

# Regex pattern for ISO 8601 timestamps
ISO_TIMESTAMP_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,3})?(Z|[+-]\d{2}:\d{2})?$")


class ValidationError(Exception):
    """Exception raised when input validation fails."""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation error for '{field}': {message}")


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """Validate an email address format.

    Args:
        email: The email address to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email address is required"

    if not isinstance(email, str):
        return False, "Email must be a string"

    if len(email) > 254:
        return False, "Email address is too long (max 254 characters)"

    if not EMAIL_PATTERN.match(email):
        return False, "Invalid email format"

    return True, None


def validate_okta_id(id_value: str, field_name: str = "ID") -> Tuple[bool, Optional[str]]:
    """Validate an Okta ID format.

    Args:
        id_value: The ID to validate
        field_name: Name of the field for error messages

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not id_value:
        return False, f"{field_name} is required"

    if not isinstance(id_value, str):
        return False, f"{field_name} must be a string"

    if len(id_value) > 100:
        return False, f"{field_name} is too long (max 100 characters)"

    if not OKTA_ID_PATTERN.match(id_value):
        return False, f"{field_name} contains invalid characters"

    return True, None


def validate_iso_timestamp(timestamp: str) -> Tuple[bool, Optional[str]]:
    """Validate an ISO 8601 timestamp format.

    Args:
        timestamp: The timestamp to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not timestamp:
        return True, None  # Optional field, empty is OK

    if not isinstance(timestamp, str):
        return False, "Timestamp must be a string"

    if not ISO_TIMESTAMP_PATTERN.match(timestamp):
        return False, "Invalid ISO 8601 timestamp format (expected: YYYY-MM-DDTHH:MM:SS.sssZ)"

    # Try to parse to ensure it's a valid date
    try:
        # Handle different timestamp formats
        timestamp_clean = timestamp.replace("Z", "+00:00")
        if "+" not in timestamp_clean and "-" not in timestamp_clean[10:]:
            timestamp_clean += "+00:00"
        datetime.fromisoformat(timestamp_clean)
    except ValueError:
        return False, "Invalid timestamp value"

    return True, None


def validate_limit(limit: Optional[int], min_val: int = 20, max_val: int = 100) -> Tuple[int, Optional[str]]:
    """Validate and constrain a limit parameter.

    Args:
        limit: The limit value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Tuple of (constrained_value, warning_message)
    """
    if limit is None:
        return min_val, None

    if not isinstance(limit, int):
        try:
            limit = int(limit)
        except (ValueError, TypeError):
            return min_val, f"Limit must be an integer, using default {min_val}"

    if limit < min_val:
        return min_val, f"Limit {limit} is below minimum ({min_val}), setting to {min_val}"

    if limit > max_val:
        return max_val, f"Limit {limit} exceeds maximum ({max_val}), setting to {max_val}"

    return limit, None


def validate_required_string(value: Optional[str], field_name: str) -> Tuple[bool, Optional[str]]:
    """Validate that a required string field is present and non-empty.

    Args:
        value: The value to validate
        field_name: Name of the field for error messages

    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None:
        return False, f"{field_name} is required"

    if not isinstance(value, str):
        return False, f"{field_name} must be a string"

    if not value.strip():
        return False, f"{field_name} cannot be empty"

    return True, None


def validate_profile_dict(profile: Optional[dict], required_fields: list | None = None) -> Tuple[bool, Optional[str]]:
    """Validate a profile dictionary.

    Args:
        profile: The profile dictionary to validate
        required_fields: List of required field names (optional)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if profile is None:
        return False, "Profile is required"

    if not isinstance(profile, dict):
        return False, "Profile must be a dictionary"

    if required_fields:
        missing = [f for f in required_fields if f not in profile or not profile[f]]
        if missing:
            return False, f"Missing required profile fields: {', '.join(missing)}"

    return True, None


def sanitize_error(error: Union[Exception, str]) -> str:
    """Sanitize an error message for safe MCP tool responses.

    Removes sensitive information like URLs containing okta.com and API tokens/keys.
    Truncates to 500 characters maximum.

    Args:
        error: An Exception or string error message

    Returns:
        A sanitized error string safe for MCP tool responses
    """
    # Extract message from Exception if needed
    if isinstance(error, Exception):
        message = str(error)
    else:
        message = error

    # Strip URLs containing okta.com (they leak org URLs)
    message = re.sub(r"https?://[^\s]*okta\.com[^\s]*", "[OKTA_URL]", message, flags=re.IGNORECASE)

    # Strip Bearer tokens and API keys (pattern: Bearer followed by alphanumeric/special chars)
    message = re.sub(r"Bearer\s+[^\s]+", "[BEARER_TOKEN]", message, flags=re.IGNORECASE)

    # Strip other common API key patterns (sk_, pk_, etc.)
    message = re.sub(r"\b(sk|pk|api|key)_[a-zA-Z0-9_-]{20,}", "[API_KEY]", message, flags=re.IGNORECASE)

    # Truncate to 500 chars max
    if len(message) > 500:
        message = message[:497] + "..."

    return message
