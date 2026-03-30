from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.auth0 import AuthenticatedUser, get_current_user, require_scopes
from app.db.session import get_db_session
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import UserAlreadyExistsError, UserService

router = APIRouter()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    session: AsyncSession = Depends(get_db_session),
    _: AuthenticatedUser = Depends(require_scopes("create:users")),
) -> UserRead:
    service = UserService(repository=UserRepository(session=session))
    try:
        return await service.register_user(payload)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/me")
async def get_me(current_user: AuthenticatedUser = Depends(get_current_user)) -> dict[str, object]:
    return {
        "sub": current_user.sub,
        "scopes": current_user.scopes,
        "claims": current_user.raw_token,
    }
