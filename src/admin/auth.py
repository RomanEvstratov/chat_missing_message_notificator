from datetime import datetime, timedelta, UTC
from jose import jwt, ExpiredSignatureError
from fastapi import Request, HTTPException
from pydantic import SecretStr
from sqladmin.authentication import AuthenticationBackend
from fastapi import status

from src.admin.schemes import LoginScheme
from src.settings import settings


class AdminAuth(AuthenticationBackend):
    access_token: SecretStr | None = None

    @staticmethod
    def create_access_token(data: dict[str, str]) -> SecretStr:
        """Создание токена"""
        if data is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ошибка создания токена",
            )
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(minutes=settings.AUTH.EXPIRE)
        to_encode.update({"exp": expire})
        return SecretStr(
            jwt.encode(
                claims=to_encode, key=settings.AUTH.SECRET_KEY.get_secret_value(), algorithm=settings.AUTH.ALGORITHM
            )
        )


    async def login(
        self,
        request: Request,
    ) -> bool:
        form = await request.form()
        login = LoginScheme(
            username=form["username"],
            password=SecretStr(form["password"]),
        )

        if settings.AUTH.ADMIN_USERNAME == login.username and settings.AUTH.ADMIN_PASSWORD.get_secret_value() == login.password.get_secret_value():
            self.access_token = self.create_access_token(data={"sub": login.username})
            request.session.update({"access_token": self.access_token.get_secret_value()})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(
        self,
        request: Request,
    ) -> bool:
        try:
            access_token = request.session.get("access_token")
            if not access_token or not self.access_token or access_token != self.access_token.get_secret_value():
                return False
            jwt.decode(self.access_token.get_secret_value(), settings.AUTH.SECRET_KEY.get_secret_value(), settings.AUTH.ALGORITHM)
            return True
        except ExpiredSignatureError as exc:
            return False


authentication_backend = AdminAuth(secret_key=settings.AUTH.SECRET_KEY.get_secret_value())
