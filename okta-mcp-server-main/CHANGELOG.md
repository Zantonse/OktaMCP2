# Changelog
All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed
- Added input validation (validate_okta_id) to all tool functions accepting ID parameters
- Replaced inline limit clamping with shared validate_limit() utility across all list functions
- Sanitized all error responses with sanitize_error() to prevent Okta URL/token leakage
- Standardized ctx: Context as first parameter in all tool function signatures
- Expanded retryable exceptions to include httpx.TimeoutException and httpx.ConnectError

### Added
- sanitize_error() utility function in validators.py
- Test coverage for response.py, client.py, and retry.py utilities

## v1.0.0

- Initial release of the self hosted okta-mcp-server.
