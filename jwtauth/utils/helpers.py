import secrets
import jwt
import datetime
from fastapi_jwtauth.jwtauth.services import (get_refresh_details,
                                              get_user,
                                              logout_jwt_service)


def generate_access_token(secret_key, username, access_token_expiry, data:dict, algorithm):
    """Generate an access token that expires in 'expires_in' minutes."""
    now = datetime.datetime.now(datetime.UTC)
    if not algorithm:
        algorithm = "HS256"
    if not secret_key:
        raise ValueError("Secret key is required.")
    if not access_token_expiry:
        access_token_expiry = 7
    expiry_time = access_token_expiry
    exp_time = now + datetime.timedelta(minutes=int(expiry_time))
    payload = {
        "exp": exp_time,
        "iat": now,
        "sub": username,
        "iss": username
    }
    payload = {**data,**payload}
    return jwt.encode(payload, secret_key, algorithm=algorithm), exp_time

def generate_refresh_token(refersh_token_expiry=None):
    """Generate a secure 32-character refresh token and store it in DB."""
    if not refersh_token_expiry:
        refersh_token_expiry = 30 #days
    now = datetime.datetime.now(datetime.UTC)
    expiry_time = refersh_token_expiry
    expires_at = now + datetime.timedelta(days=int(expiry_time))
    refresh_token = secrets.token_hex(32)  # 32-character token
    return refresh_token, expires_at

def validate_token(token, secret_key, algorithm):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        exp_time = payload.get("exp")
        if exp_time and datetime.datetime.now(datetime.UTC) > datetime.datetime.fromtimestamp(exp_time,datetime.UTc):
            subject = payload.get("sub")
            user = get_user(subject)
            return True if user else False
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False


def validate_refresh_token(username, refresh_token):
    try:
        user = get_user(username)
        if not user:
            return False
        refresh_token_details = get_refresh_details(user.id,refresh_token)
        if not refresh_token_details:
            return False, None
        return True, refresh_token_details
    except Exception as e:
        raise e
    

def jwt_logout_user(username):
    try:
        user = get_user(username)
        if not user:
            raise ValueError("User not found")
        return logout_jwt_service(user.id)
    except Exception as e:
        raise e