"""Launch uvicorn with clean logging configuration."""

import sys
import uvicorn
from app.core.log_config import LOGGING_CONFIG_SIMPLE

if __name__ == "__main__":
    # Get port from command line or use default
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    reload = "--reload" in sys.argv

    # Run uvicorn with clean logging (no ANSI colors)
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=reload,
        log_config=LOGGING_CONFIG_SIMPLE,
        access_log=True,
    )
