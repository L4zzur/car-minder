from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from api.deps import get_current_user, get_user_service
from core.config import settings
from core.models import User
from core.schemas import Token, UserRead
from core.security import create_access_token
from services import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service),
):
    user = await service.authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.auth.access_token_expire_minutes * 60,
        path="/",
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
