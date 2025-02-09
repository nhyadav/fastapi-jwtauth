import datetime
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from .base import BaseModel

class EnvVarsModel(BaseModel):
    __tablename__= "env_vars_model"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    env_name:Mapped[str] = mapped_column(String(100),nullable=False)
    env_value:Mapped[str] = mapped_column(String(100),nullable=False)
    remark:Mapped[str] = mapped_column(String(100),nullable=False)
    is_active:Mapped[bool] = mapped_column(nullable=False, default=True)

class JwtAccessTokenPayload(BaseModel):
    __tablename__ = "jwt_access_token_payload"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    payload_key:Mapped[str] = mapped_column(String(100),nullable=False)
    remarks:Mapped[str] = mapped_column(String(100),nullable=False)
    is_active:Mapped[bool] = mapped_column(nullable=False, default=True)
