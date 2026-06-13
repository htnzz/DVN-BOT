from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GisUserData:
    id: int
    full_name: str
    role: str
    phone: str
    password: str


_MOCK_GIS_USERS: tuple[GisUserData, ...] = (
    GisUserData(
        id=31,
        full_name="Иванов Иван Иванович",
        role="Мастер",
        phone="+79991112233",
        password="1234",
    ),

    GisUserData(
        id=32,
        full_name="Вазген Вазгенович",
        role="Мастер",
        phone="+79996148814",
        password="0000",
    )
)


async def authenticate_user(phone: str, password: str) -> GisUserData | None:
    normalized_phone = phone.strip()
    normalized_password = password.strip()

    for user in _MOCK_GIS_USERS:
        if user.phone == normalized_phone and user.password == normalized_password:
            return user

    return None
