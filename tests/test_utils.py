import pytest
from jwtauth.utils import (UserRegistration,
                          create_jwt_token,
                          jwt_login,
                          jwt_token_validate,
                          jwt_refresh_tokens,
                          jwt_logout,
                          get_current_user)

@pytest.fixture(autouse=True)
def setup_database():
    from jwtauth.db.database import db_config
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.declarative import declarative_base
    
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




# Test UserRegistration class
def test_user_registration_save():
    user = UserRegistration(username="testuser", password="password", confirm_password="password", email="test@example.com", first_name="Test", last_name="User")
    assert user.save() is not None  # Assuming save returns a user object or similar

def test_user_registration_update():
    user = UserRegistration(username="testuser", password="newpassword", confirm_password="newpassword", email="test@example.com", first_name="Test", last_name="User")
    assert user.update() is not None  # Assuming update returns a user object or similar

def test_user_registration_delete():
    user = UserRegistration(username="testuser")
    assert user.delete() is True  # Assuming delete returns True on success

# Test JWT functions
def test_create_jwt_token():
    token_data = create_jwt_token("testuser", "password")
    assert "access_token" in token_data
    assert "refresh_token" in token_data

def test_jwt_login():
    token_data = jwt_login("testuser", "password")
    assert "access_token" in token_data
    assert "refresh_token" in token_data

def test_jwt_token_validate():
    token = create_jwt_token("testuser", "password")["access_token"]
    assert jwt_token_validate(token) is not None

def test_jwt_refresh_tokens():
    token_data = jwt_refresh_tokens("testuser", "valid_refresh_token")
    assert "access_token" in token_data
    assert "refresh_token" in token_data

def test_jwt_logout():
    token = create_jwt_token("testuser", "password")["access_token"]
    assert jwt_logout(token) is True  # Assuming logout returns True on success

def test_get_current_user():
    token = create_jwt_token("testuser", "password")["access_token"]
    assert get_current_user(token) is not None
