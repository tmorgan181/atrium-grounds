"""Development API key auto-registration.

Automatically loads and registers dev API keys from dev-api-keys.txt if it exists.
This is for local development only - production keys should be managed via database.
"""

from pathlib import Path


def parse_dev_keys_file(file_path: Path) -> dict[str, str]:
    """
    Parse dev-api-keys.txt file for API keys.

    Args:
        file_path: Path to dev-api-keys.txt

    Returns:
        Dictionary with 'dev_key' and 'partner_key' (or empty dict if not found)
    """
    keys = {}

    try:
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("DEV_KEY="):
                    keys["dev_key"] = line.split("=", 1)[1]
                elif line.startswith("PARTNER_KEY="):
                    keys["partner_key"] = line.split("=", 1)[1]
    except FileNotFoundError:
        pass

    return keys


def auto_register_dev_keys() -> dict[str, str] | None:
    """
    Automatically register development API keys if dev-api-keys.txt exists.

    Looks for dev-api-keys.txt in the service root directory and registers
    any keys found. This only runs in development environments.

    Returns:
        Dictionary of registered keys, or None if file not found
    """
    # Only run in development (when running from source, not production container)
    dev_keys_path = Path(__file__).parent.parent.parent / "dev-api-keys.txt"

    if not dev_keys_path.exists():
        return None

    # Import here to avoid circular dependency
    from app.middleware.auth import register_api_key

    keys = parse_dev_keys_file(dev_keys_path)

    if not keys:
        return None

    # Register keys
    registered = {}

    if "dev_key" in keys:
        register_api_key(keys["dev_key"], tier="api_key")
        registered["dev_key"] = keys["dev_key"]

    if "partner_key" in keys:
        register_api_key(keys["partner_key"], tier="partner")
        registered["partner_key"] = keys["partner_key"]

    return registered
