from pathlib import Path
from typing import Any

from aiomax.bot import Bot
from botocore.exceptions import ClientError

from src.config.logger import logger
from src.services.s3_service import S3FileNotFoundError, S3Service


def get_suffix_by_mime_type(mime_type: str | None) -> str:
    match mime_type:
        case "image/png":
            return ".png"
        case "image/webp":
            return ".webp"
        case "image/jpeg" | "image/jpg":
            return ".jpg"
        case _:
            return ".jpg"


class MaxMediaService:
    def __init__(self, storage_service: S3Service) -> None:
        self.storage_service = storage_service

    async def build_image_attachment_by_file_key(
        self,
        bot: Bot,
        file_key: str,
        mime_type: str | None = None,
    ) -> Any | None:
        """
        Скачивает изображение из S3/MinIO во временный файл,
        загружает его в MAX и возвращает attachment.

        ВАЖНО:
        Этот метод НЕ отправляет сообщение пользователю.
        Он только возвращает attachment для последующего callback.answer(...).
        """
        temp_path: Path | None = None

        try:
            suffix = get_suffix_by_mime_type(mime_type)

            temp_path = await self.storage_service.download_to_temp_file(
                file_key=file_key,
                suffix=suffix,
            )

            return await bot.upload_image(str(temp_path))

        except S3FileNotFoundError:
            logger.warning(
                "Файл фото не найден в хранилище, ключ: {}",
                file_key,
            )
            return None

        except ClientError:
            logger.exception(
                "Не удалось скачать фото из хранилища, ключ: {}",
                file_key,
            )
            return None

        except Exception:
            logger.exception(
                "Не удалось подготовить фото для MAX, ключ: {}",
                file_key,
            )
            return None

        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)