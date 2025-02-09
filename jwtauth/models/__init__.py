from sqlalchemy.exc import IntegrityError
from sqlalchemy import event
from .base import Users, JwtTokens
from .env_vars_model import JwtAccessTokenPayload,EnvVarsModel
from fastapi_jwtauth.jwtauth.models import EnvVarsModel, JwtAccessTokenPayload
from fastapi_jwtauth.jwtauth.db.database import db_config

    
@event.listens_for(EnvVarsModel.__table__, "after_create")
def insert_default_env_vars(target, connection, **kwargs):
    connection.execute(
        target.insert(),
        [
            {"env_name": "ACCESS_TOKEN_EXPIRY", "env_value": "15", "remark": "Token expiry in minutes"},
            {"env_name": "REFRESH_TOKEN_EXPIRY", "env_value": "7", "remark": "Token expiry in days"},
        ],
    )

@event.listens_for(JwtAccessTokenPayload.__table__, "after_create")
def insert_default_payloads(target, connection, **kwargs):
    connection.execute(
        target.insert(),
        [
            {"payload_key": "username", "remarks": "username for token identification."},
        ],
    )

__all__ = ["Users", "JwtTokens","JwtAccessTokenPayload","EnvVarsModel"]