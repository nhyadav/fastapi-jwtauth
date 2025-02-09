# auth_package/models/base.py
import datetime
import bcrypt
from enum import Enum
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr
from sqlalchemy.sql import func
from sqlalchemy import String, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declared_attr
from fastapi_jwtauth.jwtauth.db.database import db_config

Base = db_config.get_base()

if Base is None:
    raise RuntimeError("You must configure the jwtauth package before using it.")

class BaseModel(Base):
    __abstract__ = True
    
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=func.now(), onupdate=func.now(), nullable=False
    )

class UsersModel(BaseModel):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    firstname: Mapped[str] = mapped_column(String(100),nullable=False)
    lastname: Mapped[str] = mapped_column(String(100),nullable=False)
    username: Mapped[str] = mapped_column(String(100),nullable=False)
    password: Mapped[str] = mapped_column(String(100),nullable=False)
    scopes: Mapped[str] = mapped_column(String(100),nullable=True)   # comma-separated scopes
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    def set_password(self, password: str):
        """Hash and set the password."""
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

class Users(UsersModel):
    __tablename__ = "users"



class TokenStatus(Enum):
    ACTIVE = "Active"
    EXPIRED = "Expired"

class JWTModel(BaseModel):
    """Model to save the JWT params and data."""
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    access_token: Mapped[str] = mapped_column(String(1000),nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(1000),nullable=False)
    access_expiry_time: Mapped[datetime.datetime] = mapped_column(nullable=False,comment="The time when the access token expires")
    refresh_expiry_time: Mapped[datetime.datetime] = mapped_column(nullable=False, comment="The time when the refresh token expires")
    is_revoked: Mapped[bool] = mapped_column(nullable=False, default=False, comment="The refresh token is revoked or not")
    revoked_at: Mapped[datetime.datetime] = mapped_column(nullable=True,comment="The time when the refresh token was revoked")
    status: Mapped[TokenStatus] = mapped_column(SQLEnum(TokenStatus), nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

class JwtTokens(JWTModel):
    __tablename__ = "jwttokens"
   # create all models