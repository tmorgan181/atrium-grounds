"""Export functionality for analysis results (FR-014)."""

import csv
import json
from enum import Enum
from io import StringIO
from typing import Any


class ExportFormat(str, Enum):
    """Supported export formats."""

    JSON = "json"
    CSV = "csv"
    MARKDOWN = "markdown"


class ExportFormatter:
    """Formats analysis results for export in various formats."""

    @staticmethod
    def detect_format(format_str: str) -> ExportFormat:
        """
        Detect export format from string.

        Args:
            format_str: Format string (json, csv, markdown, md)

        Returns:
            ExportFormat enum value

        Raises:
            ValueError: If format is not supported
        """
        format_lower = format_str.lower()

        if format_lower in ("markdown", "md"):
            return ExportFormat.MARKDOWN
        elif format_lower == "json":
            return ExportFormat.JSON
        elif format_lower == "csv":
            return ExportFormat.CSV
        else:
            raise ValueError(f"Unsupported export format: {format_str}")

    def to_json(self, data: dict[str, Any], pretty: bool = False) -> str:
        """
        Export analysis data to JSON format.

        Args:
            data: Analysis result dictionary
            pretty: Enable pretty printing with indentation

        Returns:
            JSON string
        """
        if pretty:
            return json.dumps(data, indent=2, default=str)
        return json.dumps(data, default=str)

    def to_csv(self, data: dict[str, Any]) -> str:
        """
        Export analysis data to CSV format.

        Flattens nested structures for CSV compatibility.

        Args:
            data: Analysis result dictionary

        Returns:
            CSV string
        """
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=self._get_csv_fields(data))
        writer.writeheader()

        # Flatten the data
        flat_data = self._flatten_dict(data)
        writer.writerow(flat_data)

        return output.getvalue()

    def to_markdown(self, data: dict[str, Any]) -> str:
        """
        Export analysis data to Markdown format.

        Args:
            data: Analysis result dictionary

        Returns:
            Markdown string
        """
        lines = []

        # Header
        lines.append("# Analysis Results")
        lines.append("")

        # Basic info
        lines.append("## Overview")
        lines.append("")
        lines.append(f"- **ID**: `{data.get('id', 'N/A')}`")
        lines.append(f"- **Status**: {data.get('status', 'N/A')}")
        lines.append(f"- **Created**: {data.get('created_at', 'N/A')}")

        if data.get("confidence_score") is not None:
            lines.append(f"- **Confidence Score**: {data['confidence_score']:.2f}")

        if data.get("processing_time") is not None:
            lines.append(f"- **Processing Time**: {data['processing_time']:.2f}s")

        lines.append("")

        # Patterns
        if data.get("patterns"):
            lines.append("## Detected Patterns")
            lines.append("")

            patterns = data["patterns"]

            if isinstance(patterns, dict):
                for pattern_type, pattern_data in patterns.items():
                    lines.append(f"### {pattern_type.capitalize()}")
                    lines.append("")

                    if isinstance(pattern_data, dict):
                        for key, value in pattern_data.items():
                            lines.append(f"- **{key}**: {value}")
                    else:
                        lines.append(f"- {pattern_data}")

                    lines.append("")

        # Conversation
        if data.get("conversation_text"):
            lines.append("## Conversation")
            lines.append("")
            lines.append("```")
            lines.append(data["conversation_text"])
            lines.append("```")
            lines.append("")

        # Expiration
        if data.get("expires_at"):
            lines.append("## Data Retention")
            lines.append("")
            lines.append(f"- **Expires**: {data['expires_at']}")
            lines.append("")

        return "\n".join(lines)

    def _flatten_dict(
        self, data: dict[str, Any], parent_key: str = "", sep: str = "."
    ) -> dict[str, Any]:
        """
        Flatten nested dictionary for CSV export.

        Args:
            data: Dictionary to flatten
            parent_key: Parent key for nested items
            sep: Separator for nested keys

        Returns:
            Flattened dictionary
        """
        items = []

        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key

            if isinstance(value, dict):
                items.extend(self._flatten_dict(value, new_key, sep=sep).items())
            elif isinstance(value, list):
                # Convert lists to JSON strings
                items.append((new_key, json.dumps(value)))
            else:
                items.append((new_key, value))

        return dict(items)

    def _get_csv_fields(self, data: dict[str, Any]) -> list:
        """
        Get CSV field names from flattened data.

        Args:
            data: Analysis result dictionary

        Returns:
            List of field names
        """
        flat_data = self._flatten_dict(data)
        return list(flat_data.keys())

    def export(self, data: dict[str, Any], format: ExportFormat, **kwargs) -> str:
        """
        Export data in specified format.

        Args:
            data: Analysis result dictionary
            format: Export format
            **kwargs: Format-specific options (e.g., pretty for JSON)

        Returns:
            Formatted export string
        """
        if format == ExportFormat.JSON:
            return self.to_json(data, pretty=kwargs.get("pretty", False))
        elif format == ExportFormat.CSV:
            return self.to_csv(data)
        elif format == ExportFormat.MARKDOWN:
            return self.to_markdown(data)
        else:
            raise ValueError(f"Unsupported format: {format}")
