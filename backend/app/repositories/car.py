from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models import Car, User


class CarRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, car: Car) -> None:
        self.session.add(car)
        await self.session.flush()

    async def delete(self, car: Car) -> None:
        await self.session.delete(car)
        await self.session.flush()

    async def get_by_id(self, car_id: UUID) -> Car | None:
        return await self.session.get(Car, car_id)

    async def get_with_user(self, car_id: UUID) -> Car | None:
        stmt = (
            select(Car)
            .where(Car.id == car_id)
            .options(selectinload(Car.user).selectinload(User.settings))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_user_id(self, user_id: UUID) -> list[Car]:
        stmt = (
            select(Car)
            .where(Car.user_id == user_id)
            .order_by(
                Car.created_at.desc(),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
