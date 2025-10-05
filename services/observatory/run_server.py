#!/usr/bin/env python
"""
Custom server runner with cleaner startup output.
Formats uvicorn messages for better readability.
"""

import sys
import logging
from pathlib import Path


class CleanFormatter(logging.Formatter):
    """Custom formatter for cleaner uvicorn output."""

    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()

        # Format watch directory message with better spacing
        if "Will watch for changes in these directories:" in msg:
            start = msg.find("[")
            end = msg.find("]")
            if start != -1 and end != -1:
                dirs_str = msg[start + 1 : end]
                dirs = [d.strip().strip("'\"") for d in dirs_str.split(",")]
                if dirs:
                    # Format each directory on its own line
                    lines = ["INFO:     Watching for changes in:"]
                    for dir_path in dirs:
                        path = Path(dir_path)
                        parts = path.parts[-3:] if len(path.parts) > 3 else path.parts
                        short_path = (
                            "\\".join(parts) if sys.platform == "win32" else "/".join(parts)
                        )
                        lines.append(f"INFO:       - ...\\{short_path}")
                    return "\n".join(lines)

        # Format running message
        if "Uvicorn running on" in msg:
            url = msg.split("on ")[-1].replace("(Press CTRL+C to quit)", "").strip()
            return f"INFO:     Server ready at {url} (Press CTRL+C to quit)"

        # Format reloader message
        if "Started reloader process" in msg:
            pid = msg.split("[")[-1].split("]")[0] if "[" in msg else "unknown"
            return f"INFO:     Hot reload active (PID: {pid})"

        # Pass through other messages
        return super().format(record)


# Setup custom formatting for uvicorn loggers
formatter = CleanFormatter()
for logger_name in ["uvicorn", "uvicorn.error"]:
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        for handler in logger.handlers:
            handler.setFormatter(formatter)

# Suppress access logs
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

# Show startup header before uvicorn initialization
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

print(f"\n{CYAN}{'=' * 70}{RESET}")
print(f"   {BOLD}{MAGENTA}⚡ STARTING ATRIUM OBSERVATORY{RESET}")
print(f"{CYAN}{'=' * 70}{RESET}\n")

# Now import and run uvicorn
import uvicorn

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    reload = "--reload" in sys.argv

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=reload,
        log_level="info",
        access_log=False,  # Suppress access logs by default
    )
