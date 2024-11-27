import asyncio
import pdb
from http.client import responses
from pprint import pprint
from uuid import UUID

import pytest
from faker.proxy import Faker
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.jwt import decode_token
from app.db.models import User
from tests.conftest import faker


@pytest.mark.asyncio
async def test_create_jwt(user_one: User, client: AsyncClient, user_one_password: str):
    """Проверяет получение пары из refresh и access токенов."""
    response = await client.post(
        "/api/v1/users/jwt/create/",
        json={
            "email": user_one.email,
            "password": user_one_password,
        },
    )

    response_json = response.json()

    pprint(response_json)

    assert response.status_code == status.HTTP_201_CREATED, "Получен код ответа отличный от ожидаемого"
    assert "access_token" in response_json, "В ответе не найден access токен"
    assert "refresh_token" in response_json, "В ответе не найден refresh токен"
    access_payload = decode_token(response_json["access_token"])
    refresh_payload = decode_token(response_json["refresh_token"])
    assert UUID(access_payload["sub"]) == user_one.id, "ID пользователя в access токене не совпадает"
    assert UUID(refresh_payload["sub"]) == user_one.id, "ID пользователя в refresh токене не совпадает"
    assert access_payload["token_type"] == "access", "Тип токена не правильный"
    assert refresh_payload["token_type"] == "refresh", "Тип токена не правильный"


@pytest.mark.asyncio
async def test_refresh_jwt(refresh_token_user_one: str, client: AsyncClient, user_one: User):
    """Тест обновления jwt токенов по refresh токену."""
    data = {
        "refresh_token": refresh_token_user_one,
    }
    response = await client.post(
        "/api/v1/users/jwt/refresh/",
        json=data,
    )

    response_json = response.json()

    pprint(response_json)

    assert response.status_code == status.HTTP_200_OK, "Получен код ответа отличный от ожидаемого"
    assert "access_token" in response_json, "В ответе не найден access токен"
    assert "refresh_token" in response_json, "В ответе не найден refresh токен"
    access_payload = decode_token(response_json["access_token"])
    refresh_payload = decode_token(response_json["refresh_token"])
    assert UUID(access_payload["sub"]) == user_one.id, "ID пользователя в access токене не совпадает"
    assert UUID(refresh_payload["sub"]) == user_one.id, "ID пользователя в refresh токене не совпадает"
    assert access_payload["token_type"] == "access", "Тип токена не правильный"
    assert refresh_payload["token_type"] == "refresh", "Тип токена не правильный"


@pytest.mark.asyncio
async def test_validate_correct_jwt(access_token_user_one: str, client: AsyncClient):
    """Тест валидации jwt токена."""
    data = {
        "token": access_token_user_one,
    }
    response = await client.post(
        "/api/v1/users/jwt/validate/",
        json=data,
    )

    response_json = response.json()

    pprint(response_json)

    assert response.status_code == status.HTTP_200_OK, "Получен код ответа отличный от ожидаемого"
    assert "validation_result" in response_json, "В ответе не найден validation_result"
    assert response_json["validation_result"] is True, "Результат валидации токена не соответствует ожидаемому"


@pytest.mark.asyncio
async def test_validate_incorrect_jwt(client: AsyncClient, faker: Faker):
    """Тест валидации jwt токена."""
    data = {
        "token": faker.linux_platform_token(),
    }
    response = await client.post(
        "/api/v1/users/jwt/validate/",
        json=data,
    )

    response_json = response.json()

    pprint(response_json)

    assert response.status_code == status.HTTP_200_OK, "Получен код ответа отличный от ожидаемого"
    assert "validation_result" in response_json, "В ответе не найден validation_result"
    assert response_json["validation_result"] is False, "Результат валидации токена не соответствует ожидаемому"


@pytest.mark.asyncio
async def test_create_user_with_valid_data(client: AsyncClient, faker: Faker, db_session: AsyncSession):
    """Проверяет создание нового пользователя с валидными данными."""
    data = {
        "email": faker.unique.email(),
        "username": faker.unique.user_name(),
        "first_name": faker.first_name(),
        "second_name": faker.last_name(),
        "middle_name": faker.middle_name(),
        "password": faker.password(),
    }
    response = await client.post("/api/v1/users/register/", json=data)
    response_json = response.json()
    pprint(response_json)
    stmt = select(User).where(User.email == data["email"])
    result = await db_session.execute(stmt)
    user: User = result.scalar_one_or_none()

    assert user.verify_password(data["password"]), "Пароль не совпадает с переданным"
    assert user.username == data["username"], "Имя пользователя не совпадает с переданным"
    assert user.email == data["email"], "Email не совпадает с переданным"
    assert user.first_name == data["first_name"], "Имя не совпадает с переданным"
    assert user.second_name == data["second_name"], "Фамилия не совпадает с переданным"
    assert user.middle_name == data["middle_name"], "Отчество не совпадает с переданным"
