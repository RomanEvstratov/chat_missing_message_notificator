from pydantic import BaseModel, ConfigDict, SecretStr


class LoginScheme(BaseModel):
    """Схема для авторизации"""

    model_config = ConfigDict(from_attributes=True)

    username: str
    password: SecretStr