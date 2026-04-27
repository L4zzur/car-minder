from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import MileageLog


class MileageLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, mileage_log: MileageLog) -> None:
        self.session.add(mileage_log)
        await self.session.flush()

    async def delete(self, mileage_log: MileageLog) -> None:
        await self.session.delete(mileage_log)
        await self.session.flush()

    async def get_by_id(self, mileage_log_id: UUID) -> MileageLog | None:
        return await self.session.get(MileageLog, mileage_log_id)

    async def list_by_car_id(self, car_id: UUID) -> list[MileageLog]:
        stmt = (
            select(MileageLog)
            .where(MileageLog.car_id == car_id)
            .order_by(MileageLog.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_for_car(self, car_id: UUID) -> MileageLog | None:
        stmt = (
            select(MileageLog)
            .where(MileageLog.car_id == car_id)
            .order_by(MileageLog.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
