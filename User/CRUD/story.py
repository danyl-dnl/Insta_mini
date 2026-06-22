from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import Setting.Models as models


async def create_story(db: AsyncSession, user_id, media_url, created_at=None, expires_at=None):
    now = datetime.utcnow()
    new_story = models.Story(
        user_id=user_id,
        media_url=media_url,
        created_at=created_at if created_at is not None else now,
        expires_at=expires_at if expires_at is not None else (now + timedelta(days=1)),
    )
    db.add(new_story)
    await db.commit()
    await db.refresh(new_story)
    return new_story


async def get_story_by_id(db: AsyncSession, story_id):
    result = await db.execute(select(models.Story).where(models.Story.story_id == story_id))
    return result.scalar_one_or_none()


async def get_active_stories_by_user(db: AsyncSession, user_id):
    result = await db.execute(select(models.User).where(models.User.user_id == user_id))
    user = result.scalar_one_or_none()
    if user:
        now = datetime.utcnow()
        return [s for s in user.stories if s.expires_at > now]
    return []

get_active_stories = get_active_stories_by_user


async def delete_story(db: AsyncSession, story_id):
    result = await db.execute(select(models.Story).where(models.Story.story_id == story_id))
    story = result.scalar_one_or_none()
    if story:
        await db.execute(delete(models.HighlightStory).where(
            models.HighlightStory.story_id == story_id
        ))
        await db.delete(story)
        await db.commit()
        return True
    return False


async def create_highlight(db: AsyncSession, user_id, title, cover_url=None):
    new_hl = models.Highlight(
        user_id=user_id,
        title=title,
        cover_url=cover_url,
        created_at=datetime.utcnow()
    )
    db.add(new_hl)
    await db.commit()
    await db.refresh(new_hl)
    return new_hl


async def get_highlight_by_id(db: AsyncSession, highlight_id):
    result = await db.execute(
        select(models.Highlight).where(models.Highlight.highlight_id == highlight_id)
    )
    return result.scalar_one_or_none()


async def get_highlights_by_user(db: AsyncSession, user_id):
    result = await db.execute(
        select(models.Highlight).where(models.Highlight.user_id == user_id)
    )
    return list(result.scalars().all())


async def update_highlight(db: AsyncSession, highlight_id, title=None, cover_url=None):
    result = await db.execute(
        select(models.Highlight).where(models.Highlight.highlight_id == highlight_id)
    )
    hl = result.scalar_one_or_none()
    if hl:
        if title is not None:
            hl.title = title
        if cover_url is not None:
            hl.cover_url = cover_url
        await db.commit()
        await db.refresh(hl)
    return hl


async def delete_highlight(db: AsyncSession, highlight_id):
    result = await db.execute(
        select(models.Highlight).where(models.Highlight.highlight_id == highlight_id)
    )
    hl = result.scalar_one_or_none()
    if hl:
        await db.execute(
            delete(models.HighlightStory).where(models.HighlightStory.highlight_id == highlight_id)
        )
        await db.execute(
            delete(models.Highlight).where(models.Highlight.highlight_id == highlight_id)
        )
        await db.commit()
        return True
    return False


async def add_story_to_highlight(db: AsyncSession, highlight_id, story_id):
    result = await db.execute(
        select(models.HighlightStory).where(
            models.HighlightStory.highlight_id == highlight_id,
            models.HighlightStory.story_id == story_id
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing
    new_hls = models.HighlightStory(highlight_id=highlight_id, story_id=story_id)
    db.add(new_hls)
    await db.commit()
    await db.refresh(new_hls)
    return new_hls


async def get_stories_in_highlight(db: AsyncSession, highlight_id):
    result = await db.execute(
        select(models.Story)
        .join(models.HighlightStory, models.Story.story_id == models.HighlightStory.story_id)
        .where(models.HighlightStory.highlight_id == highlight_id)
    )
    return list(result.scalars().all())


async def remove_story_from_highlight(db: AsyncSession, highlight_id, story_id):
    result = await db.execute(
        select(models.HighlightStory).where(
            models.HighlightStory.highlight_id == highlight_id,
            models.HighlightStory.story_id == story_id
        )
    )
    hls = result.scalar_one_or_none()
    if hls:
        await db.delete(hls)
        await db.commit()
        return True
    return False
