from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import Setting.Models as models


async def create_reel(
    db: AsyncSession, user_id: int, video_url: str, caption: str | None = None
):
    new_reel = models.Reel(
        user_id=user_id,
        video_url=video_url,
        caption=caption,
        created_at=datetime.utcnow(),
    )
    db.add(new_reel)
    await db.commit()
    await db.refresh(new_reel)
    return new_reel


async def get_reel_by_id(db: AsyncSession, reel_id: int):
    result = await db.execute(select(models.Reel).where(models.Reel.reel_id == reel_id))
    return result.scalar_one_or_none()


async def get_reels_by_user(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.Reel)
        .where(models.Reel.user_id == user_id)
        .order_by(models.Reel.created_at.desc())
    )
    return list(result.scalars().all())


async def get_all_reels(db: AsyncSession):
    result = await db.execute(
        select(models.Reel).order_by(models.Reel.created_at.desc())
    )
    return list(result.scalars().all())


async def delete_reel(db: AsyncSession, reel_id: int):
    result = await db.execute(select(models.Reel).where(models.Reel.reel_id == reel_id))
    reel = result.scalar_one_or_none()
    if reel:
        await db.delete(reel)
        await db.commit()
        return True
    return False
