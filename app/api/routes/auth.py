import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Response, WebSocketException
from fastapi.params import Form, Depends
from pydantic import BaseModel
import jwt
from fastapi import WebSocket
from starlette import status
from app.auth.models.user import User, UserInfo
from app.container import container
from datetime import datetime, timedelta, timezone
from jwt.exceptions import PyJWTError
from pydantic import EmailStr
from fastapi import Request

router = APIRouter()
load_dotenv()
secret = os.getenv("JWT_SECRET")
algorithm = os.getenv("ALGORITHM")


class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    full_name: str


@router.post("/register")
async def register(
        user_data: UserRegistration
):
    mdb = container.mdb()
    user_service = container.user_service()
    password_service = container.password_service()
    user_exists = await user_service.get_user(user_data.email)
    if user_exists:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user_data.email,
        hashed_password=password_service.get_password_hash(user_data.password),
        full_name=user_data.full_name,
        is_google_auth=False
    )
    await mdb.add_entry(new_user)

    return {"message": "Registration successful"}


class UserLogin(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login(
        user_data: UserLogin,
        response: Response
):
    user_service = container.user_service()
    password_service = container.password_service()

    user = await user_service.get_user(user_data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    is_password_correct = password_service.verify_password(
        user_data.password, user.hashed_password
    )

    if not is_password_correct:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.is_google_auth:
        raise HTTPException(status_code=400, detail="Use Google login")

    expires = datetime.now(timezone.utc) + timedelta(minutes=60*24)
    jwt_token = jwt.encode(
        {"sub": user.email, "exp": expires},
        secret,
        algorithm=algorithm,
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {jwt_token}",
        httponly=True,
        # secure=True,  # Requires HTTPS in production
        samesite="lax",
        max_age=60*60*24,
    )

    return {
        "access_token": jwt_token,
        "token_type": "bearer"
    }

@router.post("/add-user-info")
async def add_user_info(
        user_info: UserInfo,
) -> bool:
    user_service = container.user_service()
    exists = await user_service.check_user_exist(user_info.email)
    if exists:
        return await user_service.encrypt_add_user_info(user_info)
    return False

@router.get("/get-user-info")
async def get_user_info(
        email: EmailStr,
):
    user_service = container.user_service()
    exists = await user_service.check_user_exist(email)
    if exists:
      return await user_service.get_user_info_decrypted(email)

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        "access_token",
        httponly=True,
        secure=True,
        samesite="strict"
    )
    return {"message": "Logged out successfully"}


async def get_current_user(request: Request) -> User:
    user_service = container.user_service()

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        token = token.replace("Bearer ", "").strip()
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")

    except PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    user = await user_service.get_user(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    print(user)
    return user


async def get_current_user_websocket(websocket: WebSocket) -> User:
    user_service = container.user_service()

    token = websocket.cookies.get("access_token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    try:
        # Remove Bearer prefix if present
        token = token.replace("Bearer ", "").strip()
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        email = payload.get("sub")
        if not email:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    except PyJWTError as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    user = await user_service.get_user(email)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    return user


@router.get("/me")
async def get_protected_data(
        current_user: User = Depends(get_current_user)
):
    print(current_user)
    return {
        "email": current_user.email,
        "full_name": current_user.full_name
    }
