from typing import Dict, Any
from pydantic import ValidationError,validate_arguments
from fastapi_jwtauth.jwtauth.schemas import UserRegister,loginResponse
from fastapi_jwtauth.jwtauth.models import Users,JwtTokens
from fastapi_jwtauth.jwtauth.services import create_user, update_user, delete_user, check_login, save_tokens_db
from .helpers import (generate_access_token,
                     generate_refresh_token,
                     validate_token,
                     validate_refresh_token,
                     jwt_logout_user)


class UserRegistration:
    def __init__(self, 
                 username:str,
                 password:str,
                 confirm_password:str,
                 email:str,
                 first_name:str,
                 last_name:str):
        self.username = username
        self.password = password
        self.confirm_password = confirm_password
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

    def save(self):
        try:
            data = UserRegister(username=self.username,
                                password=self.password,
                                confirm_password=self.confirm_password,
                                email=self.email,
                                firstname=self.first_name,
                                lastname=self.last_name)
        except ValidationError as ve:
            raise ve
        data=data.model_dump()
        data.pop("confirm_password")
        return create_user(data)
    
    def update(self):
        if not self.username:
            raise ValueError("Username is required to update user details.")
        try:
            data = UserRegister(username=self.username,
                                password=self.password,
                                confirm_password=self.confirm_password,
                                email=self.email,
                                first_name=self.first_name,
                                last_name=self.last_name)
        except ValidationError as ve:
            raise ve
        return update_user(username=self.username, user_details=data.model_dump())

    def delete(self):
        if not self.username:
            raise ValueError("Username is required to delete user account.")
        return delete_user(username=self.username)



def create_jwt_token(username, password, data:dict=None):
    # Create a JWT token with the username and password
    response = check_login(username=username, password=password)
    if not response:
        raise ValueError("Invalid username or password.")
    if data is None:
        data = {}
    access_token, a_expiry, res_expiry = generate_access_token(username=username, data=data)
    refresh_token, r_expiry = generate_refresh_token()
    save_response = save_tokens_db(username, access_token,a_expiry,refresh_token,r_expiry)
    if save_response:
        return loginResponse(**{"access_token": access_token,
                             "refresh_token": refresh_token,
                             "token_type":"jwt",
                             "expires_in":res_expiry}).model_dump()
    raise ValueError("Something wrong in the token saving, please try again.")
    



@validate_arguments
def jwt_login(username:str, password:str, data:Dict=None) -> Dict[str,Any]:
    """
    Authenticate a user and generate JWT tokens.

    This function validates the provided username and password. If the credentials are valid,
    it creates and returns JWT access and refresh tokens. The tokens include additional
    payload data if specified.

    Args:
        username (Str): The username of the user.
        password (Str): The password of the user.
        data (Dict, optional): Additional data to include in the JWT payload.

    Returns:
        Dict[str, Any]: A dictionary containing the access token, refresh token, token type, 
        and expiration details.

    Raises:
        ValueError: If the username or password is invalid.
    """

    check_login_res = check_login(username, password)
    if not check_login_res:
        raise ValueError("Invalid username or password.")
    return create_jwt_token(username=username, password=password, data=data)
        

@validate_arguments
def jwt_token_validate(token:str) -> Dict[str, Any]:
    validation_response = validate_token(token)
    return validation_response


@validate_arguments
def jwt_refresh_tokens(username:str, refresh_token:str, grant_type:str="refresh_token") -> Dict[str, Any]:
    validation_response:bool = False
    if grant_type == "refresh_token":
        validation_response = validate_refresh_token(username,refresh_token)
    else:
        raise ValueError("Invalid grant type.")
    if not validation_response:
        raise ValueError("Invalid refresh token.")
    access_token, access_expiry, res_expiry = generate_access_token(username, validation_response)
    refresh_token, refresh_expiry = generate_refresh_token()
    save_response = save_tokens_db(username, access_token,access_expiry,refresh_token,refresh_expiry)
    if save_response:
        return loginResponse(**{"access_token": access_token,
                             "refresh_token": refresh_token,
                             "token_type":"jwt",
                             "expires_in":res_expiry}).model_dump()
    raise ValueError("Something wrong in the token saving, please try again.")


@validate_arguments
def jwt_logout(username:str) -> Dict[str,Any]:
    return jwt_logout_user(username)


