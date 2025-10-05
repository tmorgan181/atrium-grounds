"""Unit tests for API key authentication."""

import pytest
from app.middleware.auth import validate_api_key, generate_api_key, hash_api_key


def test_api_key_generation():
    """Test API key generation."""
    key = generate_api_key()

    assert len(key) == 32  # Standard API key length
    # URL-safe tokens can contain: A-Z, a-z, 0-9, -, _
    assert all(c.isalnum() or c in "-_" for c in key)


def test_api_key_hashing():
    """Test API key hashing for storage."""
    key = "test_api_key_12345"
    hashed = hash_api_key(key)

    assert hashed != key  # Should be hashed
    assert len(hashed) == 64  # SHA256 hex digest length

    # Same key should produce same hash
    assert hash_api_key(key) == hashed


def test_validate_api_key_valid():
    """Test validation of valid API key."""
    key = "valid_test_key"
    hashed = hash_api_key(key)

    # Store in mock registry
    valid_keys = {hashed: "api_key"}

    result = validate_api_key(key, valid_keys)
    assert result is True


def test_validate_api_key_invalid():
    """Test validation of invalid API key."""
    valid_keys = {hash_api_key("valid_key"): "api_key"}

    result = validate_api_key("wrong_key", valid_keys)
    assert result is False


def test_validate_api_key_empty():
    """Test validation with empty key."""
    valid_keys = {hash_api_key("valid_key"): "api_key"}

    result = validate_api_key("", valid_keys)
    assert result is False


def test_validate_api_key_none():
    """Test validation with None key."""
    valid_keys = {hash_api_key("valid_key"): "api_key"}

    result = validate_api_key(None, valid_keys)
    assert result is False
