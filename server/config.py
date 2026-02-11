from dotenv import load_dotenv
import os

# Load .env into environment
load_dotenv()

# LLM
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai") # Deafult: openai
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./library.db"
) # Default: sqlite+aiosqlite:///./library.db
