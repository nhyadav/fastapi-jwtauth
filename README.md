
## **FastAPI JWT Auth Handler**  
A lightweight and easy-to-use **JWT authentication** package for FastAPI applications. This package simplifies user authentication by providing built-in functionality for **user management, authentication, and token handling**.  

### **Features**  
✔️ User registration, update, and deletion  
✔️ Secure login & logout  
✔️ JWT-based authentication  
✔️ Refresh token support  
✔️ Automatic model creation  

---

## **Installation**  
Install the package via `pip`:  
```bash
pip install fastapi-jwtauth
```

---

## **Usage**  

### **1. Initialize the Auth Module**  
Import and initialize the authentication handler in your FastAPI app:  
```python

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi_jwtauth.jwtauth.config import configure 

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#setup the package
base=configure(Base, SessionLocal)

base.metadata.create_all(bind=engine) #create all models

```

---

### **2. User Registration**  
Register a new user with **automatic password hashing**:  
```python
from pydantic import BaseModel
from fastapi_jwtauth.jwtauth.utils import UserRegistration


class UserRegister(BaseModel):
    first_name:str
    last_name:str
    email:str
    username:str
    password:str
    confirm_password:str



@app.post("/register")
def register(userdetails:UserRegister):
    usrreg = UserRegistration(**userdetails.model_dump())
    usrreg.save()
    return {"message": "User registered successfully!"}
```

---

### **3. User Login & Token Generation**  
Authenticate users and issue JWT tokens:  
```python
from fastapi_jwtauth.jwtauth.utils import jwt_login

@app.post("/login")
def login(username:str,password:str):
    tokens = jwt_login(username,password)
    return tokens
```

---

---

### **4. Token Refresh**  
Refresh expired access tokens using a refresh token:  
```python
from fastapi_jwtauth.jwtauth.utils import jwt_refresh_tokens

@app.post("/refresh")
def refresh_tokens(request:Request, refreshtokens:RefreshTokens, db: Annotated[Session, Depends(get_db)]):
    refresh_tokens = jwt_refresh_tokens(username=refreshtokens.username, refresh_token=refreshtokens.refresh_token, grant_type=refreshtokens.grant_type)
    return refresh_tokens
```

---

### **5. User Logout**  
Invalidate user sessions and tokens:  
```python
from fastapi_jwtauth.jwtauth.utils import jwt_logout

@app.post("/logout")
def logout(token: str):
    return jwt_logout(token)
```

---

## **Configuration**  
You can customize JWT settings via environment variables or DB tables:  
```python
from fastapi_jwtauth.jwtauth.utils.jwtauth import JWTAuthHandler

auth = JWTAuthHandler(secret_key="your-secret-key", access_token_expiry=15, refresh_token_expiry=60)
```

| **Setting**  | **Description** | **Default** |
|-------------|---------------|------------|
| `secret_key` | Secret key for JWT signing | `"your-secret-key"` |
| `access_token_expiry` | Access token expiration (minutes) | `15` |
| `refresh_token_expiry` | Refresh token expiration (minutes) | `60` |

---

## **License**  
This project is licensed under the **MIT License**.  

🚀 **Easily integrate JWT authentication in your FastAPI apps!**  

---

Let me know if you need modifications or additional sections! 😊