from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import aioboto3
from botocore.exceptions import ClientError

from src.config.logger import logger
from src.config.settings import get_settings


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

                async with response["Body"] as stream:
                    return await stream.read()

        except ClientError:
            logger.exception("Ошибка скачивания из S3, код ошибки: {}", key)
            return None