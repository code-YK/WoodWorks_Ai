import os
from dotenv import load_dotenv

load_dotenv()

# LLM
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///woodworks.db")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "logs/app.log"

# PDF
RECEIPTS_DIR = "receipts"

# Graph
MAX_SUPERVISOR_STEPS = 10
COMPANY_NAME = "WoodWorks AI"
