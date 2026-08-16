from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, user: User) -> None:
        self.session.add(user)
        await self.session.flush()

    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.flush()

    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(
            func.lower(User.username) == username.strip().lower(),
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(func.lower(User.email) == email.strip().lower())
        result = await self.session.execute(stmt)
        return result.scalars().first()
