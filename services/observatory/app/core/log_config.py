"""Custom logging configuration for clean, readable logs."""

import logging
import sys
from datetime import datetime, UTC

# Custom formatter for clean, readable logs
class CleanFormatter(logging.Formatter):
    """Clean formatter without ANSI codes, with timestamps."""
    
    # Status code colors (for terminals that support them, optional)
    COLORS = {
        'INFO': '',
        'WARNING': '',
        'ERROR': '',
        'CRITICAL': '',
        'RESET': ''
    }
    
    def format(self, record):
        """Format log record cleanly."""
        # Get timestamp
        timestamp = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
        
        # Format based on record type
        if hasattr(record, 'status_code'):
            # HTTP access log
            status = record.status_code
            method = getattr(record, 'method', 'GET')
            path = getattr(record, 'path', '/')
            client = getattr(record, 'client', '?.?.?.?')
            
            # Status indicator
            if status < 300:
                indicator = '✓'
            elif status < 400:
                indicator = '→'
            elif status < 500:
                indicator = '!'
            else:
                indicator = '✗'
            
            return f"[{timestamp}] {indicator} {method:4} {path:40} {status} - {client}"
        else:
            # Regular log message
            level = record.levelname
            message = record.getMessage()
            
            # Level indicator
            indicators = {
                'INFO': 'ℹ',
                'WARNING': '⚠',
                'ERROR': '✗',
                'CRITICAL': '✗✗',
                'DEBUG': '·'
            }
            indicator = indicators.get(level, '·')
            
            return f"[{timestamp}] {indicator} {level:8} {message}"


# Uvicorn logging config without ANSI colors
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "clean": {
            "()": "app.core.log_config.CleanFormatter",
        },
        "simple": {
            "format": "[%(asctime)s] %(levelname)-8s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "clean",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "fastapi": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    }
}


# Alternative: Simple text-only config (no special characters)
LOGGING_CONFIG_SIMPLE = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[%(asctime)s] %(levelname)-8s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "uvicorn.access": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    }
}
