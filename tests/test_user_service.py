import pytest

from app.schemas.user import UserCreate
from app.services.user_service import UserAlreadyExistsError, UserService


class FakeUser:
    def __init__(self, *, id: int, email: str, full_name: str, auth0_sub: str) -> None:
        self.id = id
        self.email = email
        self.full_name = full_name
        self.auth0_sub = auth0_sub


class FakeSession:
    def __init__(self) -> None:
        self.committed = False

    async def commit(self) -> None:
        self.committed = True


class FakeUserRepository:
    def __init__(self, existing_email: str | None = None) -> None:
        self.existing_email = existing_email
        self.session = FakeSession()

    async def get_by_email(self, email: str):
        if email == self.existing_email:
            return FakeUser(id=1, email=email, full_name="Existing User", auth0_sub="auth0|existing")
        return None

    async def create(self, payload: UserCreate):
        return FakeUser(id=2, email=str(payload.email), full_name=payload.full_name, auth0_sub=payload.auth0_sub)


@pytest.mark.asyncio
async def test_register_user_success() -> None:
    repository = FakeUserRepository()
    service = UserService(repository=repository)

    result = await service.register_user(
        UserCreate(email="new@example.com", full_name="New User", auth0_sub="auth0|new")
    )

    assert result.id == 2
    assert str(result.email) == "new@example.com"
    assert repository.session.committed is True


@pytest.mark.asyncio
async def test_register_user_duplicate_email() -> None:
    repository = FakeUserRepository(existing_email="dup@example.com")
    service = UserService(repository=repository)

    with pytest.raises(UserAlreadyExistsError):
        await service.register_user(
            UserCreate(email="dup@example.com", full_name="Duplicate", auth0_sub="auth0|dup")
        )

    assert repository.session.committed is False
