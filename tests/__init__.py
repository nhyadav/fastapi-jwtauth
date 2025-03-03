import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from jwtauth.db.database import db_config

@pytest.fixture(scope="session")
def setup_database():
    # Create an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    # Configure the database
    db_config.configure(Base, TestingSessionLocal)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield

    # Clean up
    Base.metadata.drop_all(bind=engine)
