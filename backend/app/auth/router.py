"""Auth API routes — register and login."""

import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

from ..models import UserCreate, TokenResponse, ErrorResponse
from .service import create_user, authenticate_user, create_access_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
)
async def register(user: UserCreate):
    """Register a new user account."""
    try:
        create_user(user.username, user.password)
        logger.info(f"New user registered: {user.username}")
        return {"msg": "Account created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and receive a JWT access token."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": form_data.username})
    logger.info(f"User logged in: {form_data.username}")
    return TokenResponse(access_token=token)
