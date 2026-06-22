from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import Setting.Models as models


async def create_post(db: AsyncSession, user_id, caption, image_url):
    new_post = models.Post(
        user_id=user_id,
        caption=caption,
        image_url=image_url,
        created_at=datetime.utcnow(),
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return  new_post


async def get_post_by_id(db: AsyncSession, post_id):
    result = await db.execute(select(models.Post).where(models.Post.post_id == post_id))
    return result.scalar_one_or_none()


async def get_posts_by_user(db: AsyncSession, user_id):
    result = await db.execute(select(models.User).where(models.User.user_id == user_id))
    user = result.scalar_one_or_none()
    return user.posts if user else []


async def update_post_caption(db: AsyncSession, post_id, new_caption):
    result = await db.execute(select(models.Post).where(models.Post.post_id == post_id))
    post = result.scalar_one_or_none()
    if post:
        post.caption = new_caption
        await db.commit()
        await db.refresh(post)
    return post


async def update_post(db: AsyncSession, post_id, caption):
    return await update_post_caption(db, post_id, caption)


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


async def save_post(db: AsyncSession, user_id, post_id):
    existing = await db.execute(
        select(models.SavedPost).where(
            models.SavedPost.user_id == user_id,
            models.SavedPost.post_id == post_id,
        )
    )
    if existing.scalar_one_or_none():
        return None
    new_save = models.SavedPost(
        user_id=user_id,
        post_id=post_id,
        created_at=datetime.utcnow(),
    )
    db.add(new_save)
    await db.commit()
    await db.refresh(new_save)
    return new_save


async def unsave_post(db: AsyncSession, user_id, post_id):
    result = await db.execute(
        select(models.SavedPost).where(
            models.SavedPost.user_id == user_id,
            models.SavedPost.post_id == post_id,
        )
    )
    saved = result.scalar_one_or_none()
    if saved:
        await db.delete(saved)
        await db.commit()
        return True
    return False


async def get_saved_posts(db: AsyncSession, user_id):
    result = await db.execute(select(models.User).where(models.User.user_id == user_id))
    user = result.scalar_one_or_none()
    return [sp.post for sp in user.saved_posts] if user else []


async def like_post(db: AsyncSession, user_id, post_id):
    existing = await db.execute(
        select(models.PostLike).where(
            models.PostLike.user_id == user_id,
            models.PostLike.post_id == post_id,
        )
    )
    like = existing.scalar_one_or_none()
    if like:
        return like
    new_like = models.PostLike(user_id=user_id, post_id=post_id)
    db.add(new_like)
    await db.commit()
    await db.refresh(new_like)
    return new_like


async def unlike_post(db: AsyncSession, user_id, post_id):
    result = await db.execute(
        select(models.PostLike).where(
            models.PostLike.user_id == user_id,
            models.PostLike.post_id == post_id,
        )
    )
    like = result.scalar_one_or_none()
    if like:
        await db.delete(like)
        await db.commit()
        return True
    return False


async def get_likes_count(db: AsyncSession, post_id):
    result = await db.execute(select(models.Post).where(models.Post.post_id == post_id))
    post = result.scalar_one_or_none()
    return len(post.likes) if post else 0

get_post_likes_count = get_likes_count


async def get_users_who_liked_post(db: AsyncSession, post_id):
    result = await db.execute(
        select(models.User)
        .join(models.PostLike, models.User.user_id == models.PostLike.user_id)
        .where(models.PostLike.post_id == post_id)
    )
    return list(result.scalars().all())


async def add_comment(db: AsyncSession, user_id, post_id, comment_text):
    new_comment = models.PostComment(
        user_id=user_id,
        post_id=post_id,
        comment_text=comment_text,
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment


async def get_comments_for_post(db: AsyncSession, post_id):
    result = await db.execute(select(models.Post).where(models.Post.post_id == post_id))
    post = result.scalar_one_or_none()
    return post.comments if post else []


async def get_comment_by_id(db: AsyncSession, comment_id):
    result = await db.execute(
        select(models.PostComment).where(models.PostComment.comment_id == comment_id)
    )
    return result.scalar_one_or_none()


async def update_comment(db: AsyncSession, comment_id, comment_text):
    result = await db.execute(
        select(models.PostComment).where(models.PostComment.comment_id == comment_id)
    )
    comment = result.scalar_one_or_none()
    if comment:
        comment.comment_text = comment_text
        await db.commit()
        await db.refresh(comment)
    return comment


async def delete_comment(db: AsyncSession, comment_id):
    result = await db.execute(
        select(models.PostComment).where(models.PostComment.comment_id == comment_id)
    )
    comment = result.scalar_one_or_none()
    if comment:
        await db.delete(comment)
        await db.commit()
        return True
    return False


async def get_all_posts(db: AsyncSession):
    result = await db.execute(select(models.Post).order_by(models.Post.created_at.desc()))
    return list(result.scalars().all())
