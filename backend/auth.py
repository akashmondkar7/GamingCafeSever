from fastapi import HTTPException, Depends, Header
from typing import Optional
import jwt
from datetime import datetime, timedelta, timezone
import os
from models import User, UserRole

JWT_SECRET = os.environ.get('JWT_SECRET', 'your_secret_key')
JWT_ALGORITHM = 'HS256'

# Mock OTP storage (in production, use Redis)
mock_otp_storage = {}

def generate_otp(phone: str) -> str:
    """Generate mock OTP"""
    otp = "123456"
    mock_otp_storage[phone] = otp
    return otp

def verify_otp(phone: str, otp: str) -> bool:
    """Verify mock OTP"""
    stored_otp = mock_otp_storage.get(phone)
    if stored_otp == otp:
        mock_otp_storage.pop(phone, None)
        return True
    return False

def create_token(user_id: str, role: str) -> str:
    """Create JWT token"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.now(timezone.utc) + timedelta(days=30)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Dependency to get current user from token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        token = authorization.replace('Bearer ', '')
        payload = verify_token(token)
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

async def require_role(required_role: UserRole):
    """Dependency to check user role"""
    async def check_role(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get('role')
        if user_role != required_role.value:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return check_role
