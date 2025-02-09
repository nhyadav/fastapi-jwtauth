from typing import Optional
from sqlalchemy.orm import DeclarativeBase, sessionmaker

class DatabaseConfig:
    """Singleton class to manage database configuration state"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not DatabaseConfig._initialized:
            self.Base: Optional[DeclarativeBase] = None
            self.SessionLocal: Optional[sessionmaker] = None
            DatabaseConfig._initialized = True
    
    def configure(self, base: DeclarativeBase, session: sessionmaker) -> None:
        """Configure the database settings"""
        self.Base = base
        self.SessionLocal = session
        return self.Base
    
    def get_base(self) -> DeclarativeBase:
        """Get the configured Base class"""
        if self.Base is None:
            raise RuntimeError("Database Base class not configured. Call configure() first")
        return self.Base
    
    def get_session(self) -> sessionmaker:
        """Get the configured SessionLocal"""
        if self.SessionLocal is None:
            raise RuntimeError("Database Session not configured. Call configure() first")
        return self.SessionLocal


# Create a global instance
db_config = DatabaseConfig()