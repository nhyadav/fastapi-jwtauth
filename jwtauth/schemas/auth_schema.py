from pydantic import BaseModel, field_validator, EmailStr, ValidationError
from pydantic_core.core_schema import ValidationInfo

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str
    firstname: str
    lastname: str

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, confirm_password: str, values: ValidationInfo) -> str:
        if "password" in values.data and confirm_password != values.data["password"]:
            raise ValueError("Passwords do not match")
        return confirm_password


class loginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
