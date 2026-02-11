"""
Initialize database tables.

Run:
    python -m scripts.init_db
"""

from integrations.database.engine import engine, Base

# Import models so SQLAlchemy registers them
from integrations.database import (
    user_model,
    product_model,
    order_model,
)


def main():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")


if __name__ == "__main__":
    main()
