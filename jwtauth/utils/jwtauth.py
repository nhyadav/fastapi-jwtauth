from typing import Dict, Any
from pydantic import  validate_arguments
from fastapi_jwtauth.jwtauth.services import (save_tokens_db,
                                              check_login)
from fastapi_jwtauth.jwtauth.schemas import loginResponse
from .helpers import (generate_access_token,
                     generate_refresh_token,
                     validate_token,
                     validate_refresh_token,
                     jwt_logout_user)
import jwt

class JWTAuthHandler:
    def __init__(self,
                jwt_secret_key,
                jwt_algorithm,
                jwt_access_token_expiry=None,
                jwt_refresh_token_expiry=None) -> None:
        self.secret_key = jwt_secret_key
        self.algorithms = jwt_algorithm
        if not self.algorithms:
            self.algorithms = "HS256"
        self.access_token_expiry = jwt_access_token_expiry
        self.refresh_token_expiry = jwt_refresh_token_expiry
        
    
    def create_jwt_token(self, username, password, data:dict=None):
        response = check_login(username=username, password=password)
        if not response:
            raise ValueError("Invalid username or password.")
        if data is None:
            data = {}
        access_token, a_expiry = generate_access_token(secret_key=self.secret_key,
                                                                    username=username,
                                                                    access_token_expiry=self.access_token_expiry,
                                                                    data=data,
                                                                    algorithm=self.algorithms)
        refresh_token, r_expiry = generate_refresh_token(refersh_token_expiry=self.refresh_token_expiry)
        save_response = save_tokens_db(username, access_token,a_expiry,refresh_token,r_expiry)
        if save_response:
            return loginResponse(**{"access_token": access_token,
                                 "refresh_token": refresh_token,
                                 "token_type":"jwt",
                                 "expires_in":self.access_token_expiry*60}).model_dump()
        raise ValueError("Something wrong in the token saving, please try again.")
        
    @validate_arguments
    def jwt_generate_token(self, username, password, data:dict=None):
        check_login_res = check_login(username=username, password=password)
        if not check_login_res:
            raise ValueError("Invalid username or password.")
        return self.create_jwt_token(username=username, password=password, data=data)
    
    @validate_arguments
    def jwt_token_validate(self, token):
        validation_response = validate_token(token, secret_key=self.secret_key, algorithm=self.algorithms)
        return validation_response

    @validate_arguments
    def jwt_refresh_token(self, username, refresh_token, grant_type):
        validation_response:bool = False
        if grant_type == "refresh_token":
            validation_response, access_token = validate_refresh_token(username,refresh_token)
        else:
            raise ValueError("Invalid grant type.")
        if not validation_response:
            raise ValueError("Invalid refresh token.")
        data = self.get_token_payload(access_token, ignore_expiry=True)
        access_token, access_expiry = generate_access_token(secret_key=self.secret_key,
                                                                        username=username,
                                                                        access_token_expiry=self.access_token_expiry,
                                                                        data=data[0], algorithm=self.algorithms)
        refresh_token, refresh_expiry = generate_refresh_token(refersh_token_expiry=self.refresh_token_expiry)
        save_response = save_tokens_db(username, access_token,access_expiry,refresh_token,refresh_expiry)
        if save_response:
            return loginResponse(**{"access_token": access_token,
                                 "refresh_token": refresh_token,
                                 "token_type":"jwt",
                                 "expires_in":self.access_token_expiry*60}).model_dump()
        raise ValueError("Something wrong in the token saving, please try again.")
    
    @validate_arguments
    def jwt_logout(self, username):
        return jwt_logout_user(username)
        
    @validate_arguments
    def get_token_payload(self, token, ignore_expiry=False):
        """
        Decode the JWT access token and return its payload.
        
        Args:
            token (str): The JWT access token to decode
            ignore_expiry (bool, optional): If True, return the payload even if the token has expired. Defaults to False.
            
        Returns:
            dict: The decoded payload of the JWT token
            tuple: (dict, bool) - (payload, is_expired) if ignore_expiry is True
            
        Raises:
            ValueError: If the token is invalid or expired (when ignore_expiry is False)
        """
        try:
            # First try to decode normally
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithms])
            if ignore_expiry:
                return payload, False  # Token is valid and not expired
            return payload
        except jwt.ExpiredSignatureError:
            if ignore_expiry:
                # If token is expired but we want the payload anyway
                # Decode without verification to get the payload
                payload = jwt.decode(
                    token, 
                    self.secret_key, 
                    algorithms=[self.algorithms],
                    options={"verify_exp": False}
                )
                return payload, True  # Return payload and indicate it was expired
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")