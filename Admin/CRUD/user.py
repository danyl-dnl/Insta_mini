from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
import Setting.Models as models


async def get_user_by_id(db: AsyncSession, user_id):
    result = await db.execute(select(models.User).where(models.User.user_id == user_id))
    return result.scalar_one_or_none()


async def get_all_users(db: AsyncSession):
    result = await db.execute(select(models.User))
    return list(result.scalars().all())


async def delete_user(db: AsyncSession, user_id):
    result = await db.execute(select(models.User).where(models.User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return False

    await db.execute(delete(models.CloseFriend).where(
        (models.CloseFriend.user_id == user_id) | (models.CloseFriend.friend_id == user_id)
    ))
    await db.execute(delete(models.PostLike).where(models.PostLike.user_id == user_id))
    await db.execute(delete(models.PostComment).where(models.PostComment.user_id == user_id))
    await db.execute(delete(models.SavedPost).where(models.SavedPost.user_id == user_id))
    await db.execute(delete(models.UserFollower).where(
        (models.UserFollower.follower_id == user_id) | (models.UserFollower.following_id == user_id)
    ))

    story_ids = list((await db.execute(
        select(models.Story.story_id).where(models.Story.user_id == user_id)
    )).scalars().all())
    if story_ids:
        await db.execute(delete(models.HighlightStory).where(
            models.HighlightStory.story_id.in_(story_ids)
        ))

    hl_ids = list((await db.execute(
        select(models.Highlight.highlight_id).where(models.Highlight.user_id == user_id)
    )).scalars().all())
    if hl_ids:
        await db.execute(delete(models.HighlightStory).where(
            models.HighlightStory.highlight_id.in_(hl_ids)
        ))

    await db.execute(delete(models.Highlight).where(models.Highlight.user_id == user_id))
    await db.execute(delete(models.Story).where(models.Story.user_id == user_id))

    post_ids = list((await db.execute(
        select(models.Post.post_id).where(models.Post.user_id == user_id)
    )).scalars().all())
    if post_ids:
        await db.execute(delete(models.SavedPost).where(models.SavedPost.post_id.in_(post_ids)))
        await db.execute(delete(models.PostLike).where(models.PostLike.post_id.in_(post_ids)))
        await db.execute(delete(models.PostComment).where(models.PostComment.post_id.in_(post_ids)))

    await db.execute(delete(models.Post).where(models.Post.user_id == user_id))
    await db.execute(delete(models.PrivacyHistory).where(models.PrivacyHistory.user_id == user_id))
    await db.execute(delete(models.UserRole).where(models.UserRole.user_id == user_id))
    await db.execute(delete(models.UserBio).where(models.UserBio.user_id == user_id))
    await db.delete(user)
    await db.commit()
    return True
