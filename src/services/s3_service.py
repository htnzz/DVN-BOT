from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import os
import tempfile
from pathlib import Path
from typing import Any

import aioboto3
from botocore.exceptions import ClientError

from src.config.logger import logger
from src.config.settings import get_settings


class S3FileNotFoundError(Exception):
    """Файл не найден в S3/MinIO."""


class S3Service:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.session = aioboto3.Session()

        self.bucket_name = self.settings.s3_bucket_name

        self.config = {
            "endpoint_url": self.settings.s3_endpoint_url,
            "aws_access_key_id": self.settings.s3_access_key,
            "aws_secret_access_key": self.settings.s3_secret_key.get_secret_value(),
        }

    @asynccontextmanager
    async def _get_client(self) -> AsyncIterator[Any]:
        async with self.session.client("s3", **self.config) as client:
            yield client

    async def get_file(self, key: str) -> bytes | None:
        if not key:
            return None

        try:
            async with self._get_client() as client:
                response = await client.get_object(
                    Bucket=self.bucket_name,
                    Key=key,
                )

                body = response["Body"]
                try:
                    return await body.read()
                finally:
                    body.close()

        except ClientError:
            logger.exception("Ошибка скачивания из S3, ключ: {}", key)
            return None

    async def download_to_temp_file(
        self,
        file_key: str,
        suffix: str = ".jpg",
    ) -> Path:
        if not file_key:
            raise S3FileNotFoundError("Не указан ключ файла в S3/MinIO")

        fd, temp_name = tempfile.mkstemp(suffix=suffix)
        os.close(fd)

        temp_path = Path(temp_name)

        try:
            async with self._get_client() as client:
                response = await client.get_object(
                    Bucket=self.bucket_name,
                    Key=file_key,
                )

                body = response["Body"]

                try:
                    with temp_path.open("wb") as temp_file:
                        while True:
                            chunk = await body.read(1024 * 1024)

                            if not chunk:
                                break

                            temp_file.write(chunk)

                finally:
                    body.close()

            return temp_path

        except ClientError as error:
            temp_path.unlink(missing_ok=True)

            error_code = error.response.get("Error", {}).get("Code")

            if error_code in {"NoSuchKey", "404", "NotFound"}:
                logger.warning("Файл не найден в S3/MinIO, ключ: {}", file_key)
                raise S3FileNotFoundError(file_key) from error

            logger.exception("Ошибка скачивания файла из S3/MinIO, ключ: {}", file_key)
            raise

        except Exception:
            temp_path.unlink(missing_ok=True)

            logger.exception(
                "Неожиданная ошибка скачивания файла из S3/MinIO, ключ: {}",
                file_key,
            )
            raise

    async def upload_bytes(
        self,
        *,
        key: str,
        data: bytes,
        content_type: str | None = None,
    ) -> str:
        async with self._get_client() as client:
            extra_args: dict[str, Any] = {}
            if content_type:
                extra_args["ContentType"] = content_type

            await client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=data,
                **extra_args,
            )

        return key


    async def get_presigned_url(
        self,
        key: str,
        *,
        expires_in: int = 300,
    ) -> str | None:
        if not key:
            return None

        try:
            async with self._get_client() as client:
                return await client.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": self.bucket_name,
                        "Key": key,
                    },
                    ExpiresIn=expires_in,
                )

        except ClientError:
            logger.exception("Ошибка создания временной ссылки S3, ключ: {}", key)
            return None