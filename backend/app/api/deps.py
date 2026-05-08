from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import decode_access_token
from app.models import ClinicMembership, Role, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class CurrentActor:
    def __init__(self, user: User, membership: ClinicMembership) -> None:
        self.user = user
        self.membership = membership
        self.clinic_id = membership.clinic_id
        self.role = membership.role


def get_current_actor(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> CurrentActor:
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    user_id = payload.get("sub")
    clinic_id = payload.get("clinic_id")
    if not user_id or not clinic_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")

    membership = db.scalar(
        select(ClinicMembership).where(
            ClinicMembership.user_id == user_id,
            ClinicMembership.clinic_id == clinic_id,
        )
    )
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No clinic access")
    return CurrentActor(user=user, membership=membership)


def require_roles(*roles: Role) -> Callable[[CurrentActor], CurrentActor]:
    def dependency(actor: CurrentActor = Depends(get_current_actor)) -> CurrentActor:
        if actor.role == Role.OWNER_ADMIN or actor.role in roles:
            return actor
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    return dependency

