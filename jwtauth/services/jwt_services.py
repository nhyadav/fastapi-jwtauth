from datetime import datetime,UTC
from typing import Dict, List, Any
from fastapi_jwtauth.jwtauth.models import Users, JwtTokens
from fastapi_jwtauth.jwtauth.db.database import db_config

SessionLocal = db_config.get_session()



def create_user(user_details:Dict) -> Dict[str, Any]:
    """
    Create a new user with the given details.
    Args:
        user_details (dict): A dictionary of fields to update and their new values.

    Returns:
        User: The updated user object, or None if the user was not found
    """
    if SessionLocal is None:
        raise RuntimeError("You must configure the jwtauth package before using it.")
    session = SessionLocal()  # Use the globally configured session
    try:
        active_user = session.query(Users).filter(
            Users.username == user_details["username"],
            Users.is_active == True
        ).first()

        if active_user:
            raise ValueError(f"An active user with username '{user_details['username']}' already exists.")

        # Check if the email is already in use (even if the previous user is inactive)
        existing_email = session.query(Users).filter(
            Users.email == user_details["email"],
            Users.is_active == True
        ).first()

        if existing_email:
            raise ValueError(f"An account with email '{user_details['email']}' already exists.")
        user = Users(**user_details)
        user.set_password(user_details["password"])
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def update_user(username, user_details:Dict) -> Dict[str, Any]:
    """
    Update a user's information.
    
    Args:
        username (str): The username of the user to update.
        updates (dict): A dictionary of fields to update and their new values.

    Returns:
        User: The updated user object, or None if the user was not found.
    """
    if SessionLocal is None:
        raise RuntimeError("You must configure the jwtauth package before using it.")

    session = SessionLocal()
    try:
        user = session.query(Users).filter_by(username=username).first()
        if not user:
            return None
        for key, value in user_details.items():
            if hasattr(user, key) and key not in ('username'):  # Ensure the attribute exists
                setattr(user, key, value)
        session.commit()
        session.refresh(user)
        return user
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def delete_user(username:str) -> Dict[str, Any]:
    """
    Soft delete a user by setting is_active to False.
    
    Args:
        username (str): The username of the user to delete.

    Returns:
        User: The updated user object with `is_active = False`, or None if the user was not found.
    """
    if SessionLocal is None:
        raise RuntimeError("You must configure the jwt_auth package before using it.")

    session = SessionLocal()
    try:
        # Fetch the user
        user = session.query(Users).filter_by(username=username).first()
        if not user:
            return None
        user.is_active = False
        session.commit()
        session.refresh(user)
        return user
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def check_login(username, password):
    if SessionLocal is None:
        raise RuntimeError("You must configure the jwt_auth package before using it.")
    session = SessionLocal()
    try:
        user = session.query(Users).filter_by(username=username).first()
        if not user:
            return False
        if not user.check_password(password):
            return False
        return True
    except Exception as e:
        raise e

def save_tokens_db(username, access_token, access_expiry, refresh_token, refresh_expiry):
    if SessionLocal is None:
        raise RuntimeError("You must configure the jwt_auth package before using it.")
    session = SessionLocal()
    try:
        user_id = session.query(Users).filter_by(username=username).first()
        if not user_id:
            return False
        #expire the previous token if available
        prev_token = session.query(JwtTokens).filter_by(user_id=user_id.id, status="Active", is_active=1).all()
        if prev_token:
            for token in prev_token:
                token.status = "Expired"
                token.is_active = 0  
            session.commit()
        #expired all user tokens
        previous_tokens = session.query(JwtTokens).filter_by(user_id=user_id.id).all()
        if previous_tokens:
            for token in previous_tokens:
                token.status = "Expired"
                token.is_active = 0 
            session.commit()
        #save the new token
        token = JwtTokens(user_id=user_id.id,
                          access_token=access_token,
                          refresh_token=refresh_token,
                          access_expiry_time=access_expiry,
                          refresh_expiry_time=refresh_expiry,
                          is_revoked=0,
                          status="Active",
                          is_active=1)
        session.add(token)
        session.commit()
        session.refresh(token)
        return True
    except Exception as e:
        session.rollback()
        raise e

def get_env_vars():
    if SessionLocal is None:
        raise RuntimeError("You must configure the jwt_auth package before using it.")
    session = SessionLocal()
    try:
        env_var = session.query(EnvVarsModel).filter_by(is_active=1).all()
        return {row.env_name: row.env_value for row in env_var}
    except Exception as e:
        raise e
    
def get_jwt_access_payload():
    if SessionLocal is None:
        raise RuntimeError("You must configure the jwt_auth package before using it.")
    session = SessionLocal()
    try:
        payloads = session.query(JwtAccessTokenPayload).filter_by(is_active=1).all()
        return (row.payload_key for row in payloads)
    except Exception as e:
        raise e
    

def get_user(username):
    if SessionLocal is None:
        raise RuntimeError("You must configure the jwt_auth package before using it.")
    session = SessionLocal()
    try:
        user = session.query(Users).filter_by(username=username).first()
        return user
    except Exception as e:
        raise e
    
def get_refresh_details(user_id, refresh_token):
    if SessionLocal is None:
        raise RuntimeError("You must configure the jwt_auth package before using it.")
    session = SessionLocal()
    try:
        refresh_token_details = session.query(JwtTokens).filter_by(user_id=user_id,
                                                                   refresh_token=refresh_token,
                                                                   status="Active",
                                                                   is_revoked=0,
                                                                   is_active=1).first()
        if not refresh_token_details:
            return False
        #check the refresh token expiry.
        exp_time = refresh_token_details.refresh_expiry_time
        if exp_time and datetime.now(UTC) > exp_time.replace(tzinfo=UTC):
            refresh_token_details.is_revoked = 1
            refresh_token_details.revoked_at = datetime.now(UTC)
            refresh_token_details.status = "Expired"
            refresh_token_details.is_active = 0
            session.commit()
            session.refresh(refresh_token_details)
            return False
        refresh_token_details.is_revoked = 1
        refresh_token_details.revoked_at = datetime.now(UTC)
        refresh_token_details.status = "Expired"
        refresh_token_details.is_active = 0
        session.commit()
        session.refresh(refresh_token_details)
        return refresh_token_details.access_token
    except Exception as e:
        raise e

def logout_jwt_service(user_id):
    if SessionLocal is None:
        raise RuntimeError("You must configure the jwt_auth package before using it.")
    session = SessionLocal()
    try:
        user_token = session.query(JwtTokens).filter_by(user_id=user_id, is_active=1).first()
        if not user_token:
            raise ValueError("User not found.")
        user_token.status = "Expired"
        user_token.is_active = 0
        session.commit()
        session.refresh(user_token)
        return True
    except Exception as e:
        raise e