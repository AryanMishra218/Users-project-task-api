"""
This is the file you actually run: `python run.py`
It loads environment variables from .env, creates the app using
our factory function, and starts the development server.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # reads the .env file into environment variables

from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
