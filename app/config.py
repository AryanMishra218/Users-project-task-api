"""
Why this file exists:
The task guide requires "environment variables for configuration
and secrets" — never hard-code things like secret keys directly
in your code. `os.environ.get(...)` reads values from the
system's environment (which python-dotenv loads from a .env
file for local development).
"""

import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key")
    DEBUG = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
