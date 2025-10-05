"""Input validation and security filtering for conversation data."""

import re
from typing import Optional
from pydantic import BaseModel


class ValidationResult(BaseModel):
    """Result of input validation."""

    is_valid: bool
    sanitized_text: Optional[str] = None
    error: Optional[str] = None


class InputValidator:
    """
    Validates and sanitizes conversation input to prevent security issues.

    Based on SecurityMediator patterns from original Observatory:
    - SQL injection prevention
    - Command injection prevention
    - Script injection prevention (XSS)
    - Path traversal prevention
    - Null byte filtering
    - Length validation
    """

    def __init__(self, max_length: int = 10000):
        """
        Initialize validator with configuration.

        Args:
            max_length: Maximum allowed conversation length
        """
        self.max_length = max_length

        # Injection pattern detection
        self.sql_injection_patterns = [
            r"(\bDROP\b|\bDELETE\b|\bUPDATE\b|\bINSERT\b).*\bTABLE\b",
            r"--\s*$",
            r";\s*--",
            r"'\s*OR\s+'",
            r"'\s*=\s*'",
        ]

        self.cmd_injection_patterns = [
            r"\$\([^)]*\)",  # $(command)
            r"`[^`]*`",  # `command`
            r"\s&&\s",  # command chaining with AND
            r"\s\|\|\s",  # command chaining with OR
            r";\s*(ls|cat|rm|cd|mv|cp|wget|curl|sh|bash)\b",  # semicolon with command
        ]

        self.script_injection_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",  # event handlers
        ]

        self.path_traversal_patterns = [
            r"\.\./",  # ../ (directory traversal)
            r"/\.\.",  # /.. (directory traversal)
            r"\.\.$",  # .. at end of string
            r"^\.\.",  # .. at start of string
            r"[/\\]\.\.[/\\]",  # /../ or \..\  (directory traversal with slashes)
            r"/etc/",  # /etc/ access attempt
            r"\\\\",  # UNC path
        ]

    def validate(self, conversation: str) -> ValidationResult:
        """
        Validate and sanitize conversation input.

        Args:
            conversation: Raw conversation text

        Returns:
            ValidationResult with is_valid flag and sanitized text or error
        """
        # Check for None or non-string
        if conversation is None or not isinstance(conversation, str):
            return ValidationResult(is_valid=False, error="Conversation must be a string")

        # Check for empty/whitespace
        if not conversation.strip():
            return ValidationResult(is_valid=False, error="Conversation cannot be empty")

        # Check length
        if len(conversation) > self.max_length:
            return ValidationResult(
                is_valid=False,
                error=f"Conversation exceeds maximum length of {self.max_length} characters",
            )

        # Check for null bytes
        if "\x00" in conversation:
            return ValidationResult(is_valid=False, error="Conversation contains null bytes")

        # Check for SQL injection
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, conversation, re.IGNORECASE):
                return ValidationResult(is_valid=False, error="Potential SQL injection detected")

        # Check for command injection
        for pattern in self.cmd_injection_patterns:
            if re.search(pattern, conversation):
                return ValidationResult(
                    is_valid=False, error="Potential command injection detected"
                )

        # Check for script injection
        for pattern in self.script_injection_patterns:
            if re.search(pattern, conversation, re.IGNORECASE):
                return ValidationResult(is_valid=False, error="Potential script injection detected")

        # Check for path traversal
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, conversation):
                return ValidationResult(is_valid=False, error="Potential path traversal detected")

        # If all checks pass, return sanitized text
        # For now, sanitization is minimal (just strip)
        sanitized = conversation.strip()

        return ValidationResult(is_valid=True, sanitized_text=sanitized)

    def sanitize_html_entities(self, text: str) -> str:
        """
        Sanitize HTML entities for safe display.

        Args:
            text: Text potentially containing HTML entities

        Returns:
            Text with HTML entities preserved (not escaped further)
        """
        # Allow safe HTML entities like &gt;, &lt;, &amp;
        # This is for display purposes, not storage
        return text
