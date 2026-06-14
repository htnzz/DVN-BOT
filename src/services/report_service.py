import uuid

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.db.uow import UoW
from src.services.s3_service import S3Service


class ReportService:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage_service: S3Service,
    ) -> None:
        self._session_factory = session_factory
        self._storage_service = storage_service

    async def create_report(
        self,
        *,
        max_id: int,
        object_id: uuid.UUID,
        text: str,
        image: bytes | None = None,
        image_content_type: str | None = None,
    ) -> bool:
        async with UoW(self._session_factory) as uow:
            user = await uow.users.get_by_messenger_user_id(str(max_id))
            if user is None:
                return False

            object_ref = await uow.object_refs.get_by_id_and_responsible_id(
                object_id=object_id,
                responsible_id=user.id,
            )
            if object_ref is None:
                return False

            attachment_key = None
            if image is not None:
                report_number = await uow.reports.count_by_object_ref_id(object_ref.id) + 1
                attachment_key = f"objects/{object_ref.id}/report{report_number}/image.jpg"
                await self._storage_service.upload_bytes(
                    key=attachment_key,
                    data=image,
                    content_type=image_content_type or "image/jpeg",
                )

            await uow.reports.create(
                object_ref_id=object_ref.id,
                author_id=user.id,
                text=text,
                attachment_key=attachment_key,
            )
            return True