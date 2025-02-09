
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
pip install fastapi-jwtauth-handler
```

---

## **Usage**  

### **1. Initialize the Auth Module**  
Import and initialize the authentication handler in your FastAPI app:  
```python
from fastapi import FastAPI, Depends
from fastapi_jwtauth_handler import AuthHandler, UserModel

app = FastAPI()
auth = AuthHandler()

# Initialize models (if using a database)
auth.init_models()
```

---

### **2. User Registration**  
Register a new user with **automatic password hashing**:  
```python
@app.post("/register")
def register(user: UserModel):
    return auth.register_user(user)
```

---

### **3. User Login & Token Generation**  
Authenticate users and issue JWT tokens:  
```python
@app.post("/login")
def login(user: UserModel):
    return auth.login_user(user)
```

---

### **4. Protected Routes (JWT Required)**  
Secure API endpoints using JWT authentication:  
```python
@app.get("/protected")
def protected_route(user=Depends(auth.get_current_user)):
    return {"message": "You have access!", "user": user}
```

---

### **5. Token Refresh**  
Refresh expired access tokens using a refresh token:  
```python
@app.post("/refresh")
def refresh_token(token: str):
    return auth.refresh_token(token)
```

---

### **6. User Logout**  
Invalidate user sessions and tokens:  
```python
@app.post("/logout")
def logout(token: str):
    return auth.logout_user(token)
```

---

## **Configuration**  
You can customize JWT settings via environment variables or a config file:  
```python
auth = AuthHandler(secret_key="your-secret-key", access_token_expiry=15, refresh_token_expiry=60)
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