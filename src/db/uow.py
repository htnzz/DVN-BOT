from __future__ import annotations

import inspect
import re
from types import ModuleType, TracebackType
from typing import Any, Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.db.session import async_session_maker

_REPOSITORY_SUFFIX = "Repository"
_EXCLUDED_REPOSITORY_NAMES = {"BaseRepository", "Repository"}


def _camel_to_snake(value: str) -> str:
    value = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", value)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value).lower()


def _pluralize(value: str) -> str:
    if value.endswith("y") and (len(value) == 1 or value[-2] not in "aeiou"):
        return f"{value[:-1]}ies"

    if value.endswith(("s", "x", "z", "ch", "sh")):
        return f"{value}es"

    return f"{value}s"


def _repository_attr_name(repository_name: str) -> str:
    entity_name = repository_name.removesuffix(_REPOSITORY_SUFFIX)
    return _pluralize(_camel_to_snake(entity_name))


def _load_repository_module() -> ModuleType | None:
    try:
        import src.db.repositories as repositories
    except ModuleNotFoundError as exc:
        if exc.name == "src.db.repositories":
            return None
        raise

    return repositories


def _collect_repository_classes() -> dict[str, type[Any]]:
    repositories = _load_repository_module()
    if repositories is None:
        return {}

    repository_classes: dict[str, type[Any]] = {}

    for repository_name, repository_class in inspect.getmembers(repositories, inspect.isclass):
        if repository_name in _EXCLUDED_REPOSITORY_NAMES:
            continue

        if not repository_name.endswith(_REPOSITORY_SUFFIX):
            continue

        if not repository_class.__module__.startswith(repositories.__name__):
            continue

        repository_classes[_repository_attr_name(repository_name)] = repository_class

    return repository_classes


class UoW:
    def __init__(
        self,
        session_maker: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> None:
        self._session_maker = session_maker
        self._session: AsyncSession | None = None
        self._repositories = _collect_repository_classes()

        for repository_attr in self._repositories:
            setattr(self, repository_attr, None)

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("UoW не запущен")

        return self._session

    async def __aenter__(self) -> Self:
        if self._session is not None:
            raise RuntimeError("UoW уже запущен")

        self._session = self._session_maker()

        try:
            for repository_attr, repository_class in self._repositories.items():
                setattr(self, repository_attr, repository_class(self.session))
        except Exception:
            await self._close()
            raise

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._session is None:
            return

        try:
            if exc_type is None:
                await self.commit()
            else:
                await self.rollback()
        finally:
            await self._close()

    async def commit(self) -> None:
        try:
            await self.session.commit()
        except Exception:
            await self.rollback()
            raise

    async def rollback(self) -> None:
        await self.session.rollback()

    async def _close(self) -> None:
        for repository_attr in self._repositories:
            setattr(self, repository_attr, None)

        if self._session is not None:
            await self._session.close()
            self._session = None
