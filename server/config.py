# from pydantic import BaseModel
# from dotenv import load_dotenv
# import os

# # Read .env
# load_dotenv()


# class Settings(BaseModel):
#     # LLM
#     LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai") # default to "openai"
#     OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")

#     # Database
#     DATABASE_URL: str = os.getenv(
#         "DATABASE_URL",
#         "sqlite+aiosqlite:///./library.db"
#     )

#     # App
#     APP_NAME: str = "Library Desk Agent"
#     DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"


# settings = Settings()

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



# App
# APP_NAME = "Library Desk Agent"
# DEBUG = os.getenv("DEBUG", "false").lower() == "true"
