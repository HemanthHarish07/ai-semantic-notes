import os
from dotenv import load_dotenv

# Load .env from project root if present
load_dotenv()

# Required config keys (provide sensible defaults for local dev)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "none")
