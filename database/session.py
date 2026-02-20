import logging
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config.settings import DATABASE_URL
from database.models import Base

logger = logging.getLogger(__name__)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized.")


@contextmanager
def get_session() -> Session:
    session = SessionLocal()
    try:
        yield session
        session.commit()
        logger.debug("DB session committed.")
    except Exception as e:
        session.rollback()
        logger.error(f"DB session rollback due to error: {e}")
        raise
    finally:
        session.close()
