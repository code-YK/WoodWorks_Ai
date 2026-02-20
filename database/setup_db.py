import sys
import os

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.session import init_db
from database.seed_data import seed_products
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting database setup...")
    try:
        init_db()
        logger.info("Database initialized.")
        seed_products()
        logger.info("Data seeded successfully.")
    except Exception as e:
        logger.error(f"Error during database setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
