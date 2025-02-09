import os
import secrets
import jwt
import datetime
from dotenv import load_dotenv
from fastapi_jwtauth.jwtauth.services import (get_jwt_access_payload,
                                            get_env_vars,
                                            get_refresh_details,
                                            get_user,
                                            logout_jwt_service)


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def generate_access_token(username, data:dict):
    """Generate an access token that expires in 'expires_in' minutes."""
    now = datetime.datetime.now(datetime.UTC)
    env_vars = get_env_vars()
    expiry_time = env_vars.get("ACCEESS_TOKEN_EXPIRY") or os.getenv("ACCEESS_TOKEN_EXPIRY")
    exp_time = now + datetime.timedelta(minutes=int(expiry_time))
    payload = {
        "exp": exp_time,
        "iat": now,
        "sub": username,
        "iss": username
    }
    payloads_field = get_jwt_access_payload()
    if not all(key in data.keys() for key in payloads_field):
        raise ValueError("Some Parameters data are missing in jwt payload.")
    payload = {**{key:data.get(key) for key in payloads_field},**payload}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM), exp_time, int(expiry_time)*60

def generate_refresh_token():
    """Generate a secure 32-character refresh token and store it in DB."""
    now = datetime.datetime.now(datetime.UTC)
    env_vars = get_env_vars()
    expiry_time = env_vars.get("REFRESH_TOKEN_EXPIRY") or os.getenv("REFRESH_TOKEN_EXPIRY")
    expires_at = now + datetime.timedelta(days=int(expiry_time))
    refresh_token = secrets.token_hex(32)  # 32-character token
    return refresh_token, expires_at

    validation_response = validate_token(token)
def validate_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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
            return False
        #generate the new token.
        payload = jwt.decode(refresh_token_details,
                             key=SECRET_KEY,algorithms=[ALGORITHM],
                             options={"verify_exp": False})
        #remove the exp and iat from the payload
        payload.pop("exp")
        payload.pop("iat")
        #generate the new token
        return payload
    except Exception as e:
        raise e
    
def jwt_logout_user(username):
    try:
        user = get_user(username)
        if not user:
            raise   ValueError("User not found")
        return logout_jwt_service(user.id)
    except Exception as e:
        raise e