from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, payload: UserCreate) -> User:
        user = User(email=payload.email, full_name=payload.full_name, auth0_sub=payload.auth0_sub)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user
