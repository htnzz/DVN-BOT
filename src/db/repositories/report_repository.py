from sqlalchemy import func, select

from src.db.models.report import Report
from src.db.repositories.base import BaseRepository


class ReportRepository(BaseRepository[Report]):
    model = Report

    async def count_by_object_ref_id(self, object_ref_id) -> int:
        stmt = select(func.count()).select_from(Report).where(Report.object_ref_id == object_ref_id)
        result = await self.session.scalar(stmt)
        return int(result or 0)
