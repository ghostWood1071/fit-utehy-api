from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserRead


class UserAlreadyExistsError(Exception):
    pass


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def register_user(self, payload: UserCreate) -> UserRead:
        existing_user = await self.repository.get_by_email(str(payload.email))
        if existing_user is not None:
            raise UserAlreadyExistsError(f"User with email '{payload.email}' already exists")

        user = await self.repository.create(payload)
        await self.repository.session.commit()
        return UserRead.model_validate(user)
