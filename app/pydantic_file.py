from pydantic import BaseModel, Field
from typing import List


class LoginPassword(BaseModel):
    login: str = Field(..., min_length=1, description="Логин должен быть >= 1 символов")
    password : str = Field(..., min_length=6, description="Пароль должен быть >= 6 символов")

class AddTask(BaseModel):
    username: str = Field(..., min_length=1, description="Минимальная длина имени = 1")
    tasks: List[str] = Field(..., min_length=1, description="Список задач не может быть пустым")

class IdDel(BaseModel):
    id : List[int] = Field(..., min_length=1,description="Список Id не может быть пустым")

class NameDel(BaseModel):
    username : str = Field(...,min_length=1, description="Имя на удаление не должно быть пустым")

