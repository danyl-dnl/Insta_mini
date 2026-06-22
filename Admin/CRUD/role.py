from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import Setting.Models as models


async def create_role(db: AsyncSession, role_name):
    new_role = models.Role(role_name=role_name)
    db.add(new_role)
    await db.commit()
    await db.refresh(new_role)
    return new_role


async def get_role_by_id(db: AsyncSession, role_id):
    result = await db.execute(select(models.Role).where(models.Role.role_id == role_id))
    return result.scalar_one_or_none()


async def get_role_by_name(db: AsyncSession, role_name):
    result = await db.execute(select(models.Role).where(models.Role.role_name == role_name))
    return result.scalar_one_or_none()


async def update_role(db: AsyncSession, role_id, new_role_name):
    result = await db.execute(select(models.Role).where(models.Role.role_id == role_id))
    role = result.scalar_one_or_none()
    if role:
        role.role_name = new_role_name
        await db.commit()
        await db.refresh(role)
    return role


async def delete_role(db: AsyncSession, role_id):
    result = await db.execute(select(models.Role).where(models.Role.role_id == role_id))
    role = result.scalar_one_or_none()
    if role:
        await db.delete(role)
        await db.commit()
        return True
    return False
