from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
import Setting.Models as models


async def get_post_by_id(db: AsyncSession, post_id):
    result = await db.execute(select(models.Post).where(models.Post.post_id == post_id))
    return result.scalar_one_or_none()


async def get_all_posts(db: AsyncSession):
    result = await db.execute(select(models.Post).order_by(models.Post.created_at.desc()))
    return list(result.scalars().all())


async def delete_post(db: AsyncSession, post_id):
    result = await db.execute(select(models.Post).where(models.Post.post_id == post_id))
    post = result.scalar_one_or_none()
    if post:
        await db.execute(delete(models.SavedPost).where(models.SavedPost.post_id == post_id))
        await db.execute(delete(models.PostLike).where(models.PostLike.post_id == post_id))
        await db.execute(delete(models.PostComment).where(models.PostComment.post_id == post_id))
        await db.delete(post)
        await db.commit()
        return True
    return False
