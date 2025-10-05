#!/usr/bin/env python
"""
Custom server runner with cleaner startup output.
Suppresses uvicorn's initial INFO messages and shows our banner first.
"""
import sys
import logging

# Suppress uvicorn startup messages
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
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
