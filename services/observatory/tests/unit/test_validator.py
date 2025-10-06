"""Unit tests for the input validator (SecurityMediator patterns)."""

import pytest

from app.core.validator import InputValidator


@pytest.fixture
def validator():
    """Create input validator instance."""
    return InputValidator(max_length=10000)


def test_validator_initialization(validator):
    """Test that validator initializes correctly."""
    assert validator is not None
    assert validator.max_length == 10000


def test_validate_normal_conversation(validator):
    """Test validation of normal conversation."""
    conversation = """
    Human: Hello, how are you?
    AI: I'm doing well, thank you for asking!
    """

    result = validator.validate(conversation)
    assert result.is_valid is True
    assert result.sanitized_text == conversation.strip()


def test_validate_length_limit(validator):
    """Test length validation."""
    # Valid length
    short_text = "A" * 5000
    assert validator.validate(short_text).is_valid is True

    # Invalid length
    long_text = "A" * 15000
    result = validator.validate(long_text)
    assert result.is_valid is False
    assert "length" in result.error.lower()


def test_validate_injection_patterns(validator):
    """Test detection of injection patterns."""
    # SQL injection attempt
    sql_injection = "Human: '; DROP TABLE conversations; --"
    result = validator.validate(sql_injection)
    assert result.is_valid is False
    assert "injection" in result.error.lower()

    # Command injection attempt
    cmd_injection = "Human: $(rm -rf /)"
    result = validator.validate(cmd_injection)
    assert result.is_valid is False
    assert "injection" in result.error.lower()


def test_validate_script_injection(validator):
    """Test detection of script injection."""
    script_injection = "Human: <script>alert('xss')</script>"
    result = validator.validate(script_injection)
    assert result.is_valid is False
    assert "injection" in result.error.lower() or "script" in result.error.lower()


def test_validate_null_bytes(validator):
    """Test detection of null bytes."""
    null_byte_text = "Human: Hello\x00World"
    result = validator.validate(null_byte_text)
    assert result.is_valid is False


def test_validate_empty_input(validator):
    """Test validation of empty input."""
    result = validator.validate("")
    assert result.is_valid is False
    assert "empty" in result.error.lower()


def test_validate_whitespace_only(validator):
    """Test validation of whitespace-only input."""
    result = validator.validate("   \n\t  ")
    assert result.is_valid is False
    assert "empty" in result.error.lower()


def test_sanitize_safe_html(validator):
    """Test sanitization of safe HTML entities."""
    text_with_entities = "Human: What's 2 &gt; 1?"
    result = validator.validate(text_with_entities)
    assert result.is_valid is True


def test_validate_unicode_handling(validator):
    """Test handling of unicode characters."""
    unicode_text = "Human: Hello in Japanese (Konnichiwa) - testing unicode"
    result = validator.validate(unicode_text)
    assert result.is_valid is True


def test_validate_path_traversal(validator):
    """Test detection of path traversal attempts."""
    path_traversal = "Human: ../../etc/passwd"
    result = validator.validate(path_traversal)
    assert result.is_valid is False
    assert "traversal" in result.error.lower() or "path" in result.error.lower()


def test_validate_multiple_issues(validator):
    """Test that validator catches first critical issue."""
    # Both too long AND contains injection
    bad_text = "A" * 15000 + "'; DROP TABLE--"
    result = validator.validate(bad_text)
    assert result.is_valid is False
    # Should report at least one issue
    assert result.error is not None


def test_custom_max_length():
    """Test validator with custom max length."""
    short_validator = InputValidator(max_length=100)
    text = "A" * 150

    result = short_validator.validate(text)
    assert result.is_valid is False
    assert "length" in result.error.lower()
