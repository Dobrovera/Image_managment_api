from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.libs.database.database import get_db
from .auth_dto import LoginDto, RegisterDto, Token
from .auth_service import service_register, service_login


auth_router = APIRouter(prefix="/auth")


@auth_router.post("/register", response_model=Token)
async def register(user_data: RegisterDto, db: Session = Depends(get_db)):
    """
    Роут для регистрации новых юзеров.
    Пример curl-запроса:
        ```
            curl -X POST "http://localhost:8000/auth/register"
            -H "Content-Type: application/json"
            -d '{
                   "username": "testuser",
                   "password": "testpassword!"
                 }'
        ```
    """
    return await service_register(user_data, db)


@auth_router.post("/login", response_model=Token)
async def login(user_data: LoginDto, db: Session = Depends(get_db)):
    """
    Роут для логина

    Пример curl-запроса:
    ```
    curl -X POST "http://localhost:8000/auth/login"
     -H "Content-Type: application/json"
     -d '{
           "username": "testuser",
           "password": "testpassword!"
         }'
    ```
    """
    return await service_login(user_data, db)
