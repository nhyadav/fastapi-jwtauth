from fastapi_jwtauth.jwtauth.db.database import db_config

def configure_db(base, session):
    """Configure the auth package with database settings"""
    base = db_config.configure(base, session)
    from fastapi_jwtauth.jwtauth.models import Users, JwtTokens
    return base