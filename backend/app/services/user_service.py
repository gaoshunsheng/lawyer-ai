from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models import Tenant, User


async def create_user(db: AsyncSession, username: str, email: str, password: str, real_name: str | None = None) -> User:
    result = await db.execute(select(Tenant).where(Tenant.name == "Default"))
    tenant = result.scalar_one_or_none()
    if not tenant:
        tenant = Tenant(name="Default", plan="pro", status="active")
        db.add(tenant)
        await db.flush()

    user = User(
        tenant_id=tenant.id,
        username=username,
        email=email,
        password_hash=hash_password(password),
        real_name=real_name,
        role="tenant_admin",
    )
    db.add(user)
    await db.flush()
    return user


async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user
