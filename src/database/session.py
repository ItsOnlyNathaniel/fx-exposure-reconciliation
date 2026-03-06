from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///recon.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Session error, rolling back: {e}")
        raise
    finally:
        session.close()


def init_db():
    from src.database.models import Trade, ReconciliationRun, Break, AuditLog
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialised successfully")