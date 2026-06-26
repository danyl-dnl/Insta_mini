from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import Setting.Models as models
from Setting.Security import hash_password


async def create_user(
    db: AsyncSession, username, email, password, full_name=None, profile_picture=None
):
    new_user = models.User(
        username=username,
        email=email,
        password=hash_password(password),
        full_name=full_name,
        profile_picture=profile_picture,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    role_result = await db.execute(
        select(models.Role).where(models.Role.role_name == "User")
    )
    user_role = role_result.scalar_one_or_none()

    if user_role:
        new_ur = models.UserRole(
            user_id=new_user.user_id,
            role_id=user_role.role_id,
            created_at=datetime.utcnow(),
        )
        db.add(new_ur)
        await db.commit()
        await db.refresh(new_ur)

    return new_user


async def get_user_by_id(db: AsyncSession, user_id):
    result = await db.execute(select(models.User).where(models.User.user_id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username):
    result = await db.execute(
        select(models.User).where(models.User.username == username)
    )
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email):
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, user_id, full_name=None, profile_picture=None):
    result = await db.execute(select(models.User).where(models.User.user_id == user_id))
    user = result.scalar_one_or_none()
    if user:
        if full_name is not None:
            user.full_name = full_name
        if profile_picture is not None:
            user.profile_picture = profile_picture
        user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id):
    result = await db.execute(select(models.User).where(models.User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return False

    await db.execute(
        delete(models.CloseFriend).where(
            (models.CloseFriend.user_id == user_id)
            | (models.CloseFriend.friend_id == user_id)
        )
    )
    await db.execute(delete(models.PostLike).where(models.PostLike.user_id == user_id))
    await db.execute(
        delete(models.PostComment).where(models.PostComment.user_id == user_id)
    )
    await db.execute(
        delete(models.SavedPost).where(models.SavedPost.user_id == user_id)
    )
    await db.execute(
        delete(models.UserFollower).where(
            (models.UserFollower.follower_id == user_id)
            | (models.UserFollower.following_id == user_id)
        )
    )

    story_ids = list(
        (
            await db.execute(
                select(models.Story.story_id).where(models.Story.user_id == user_id)
            )
        )
        .scalars()
        .all()
    )
    if story_ids:
        await db.execute(
            delete(models.HighlightStory).where(
                models.HighlightStory.story_id.in_(story_ids)
            )
        )

    hl_ids = list(
        (
            await db.execute(
                select(models.Highlight.highlight_id).where(
                    models.Highlight.user_id == user_id
                )
            )
        )
        .scalars()
        .all()
    )
    if hl_ids:
        await db.execute(
            delete(models.HighlightStory).where(
                models.HighlightStory.highlight_id.in_(hl_ids)
            )
        )

    await db.execute(
        delete(models.Highlight).where(models.Highlight.user_id == user_id)
    )
    await db.execute(delete(models.Story).where(models.Story.user_id == user_id))

    post_ids = list(
        (
            await db.execute(
                select(models.Post.post_id).where(models.Post.user_id == user_id)
            )
        )
        .scalars()
        .all()
    )
    if post_ids:
        await db.execute(
            delete(models.SavedPost).where(models.SavedPost.post_id.in_(post_ids))
        )
        await db.execute(
            delete(models.PostLike).where(models.PostLike.post_id.in_(post_ids))
        )
        await db.execute(
            delete(models.PostComment).where(models.PostComment.post_id.in_(post_ids))
        )

    await db.execute(delete(models.Post).where(models.Post.user_id == user_id))
    await db.execute(
        delete(models.PrivacyHistory).where(models.PrivacyHistory.user_id == user_id)
    )
    await db.execute(delete(models.UserRole).where(models.UserRole.user_id == user_id))
    await db.execute(delete(models.UserBio).where(models.UserBio.user_id == user_id))
    await db.delete(user)
    await db.commit()
    return True


async def create_user_bio(db: AsyncSession, user_id, bio_text, is_active=False):
    if is_active:
        others = await db.execute(
            select(models.UserBio).where(
                models.UserBio.user_id == user_id, models.UserBio.is_active == True
            )
        )
        for other in others.scalars().all():
            other.is_active = False
    new_bio = models.UserBio(user_id=user_id, bio_text=bio_text, is_active=is_active)
    db.add(new_bio)
    await db.commit()
    await db.refresh(new_bio)
    return new_bio


async def get_user_bio_by_id(db: AsyncSession, bio_id):
    result = await db.execute(
        select(models.UserBio).where(models.UserBio.bio_id == bio_id)
    )
    return result.scalar_one_or_none()


async def get_active_user_bio(db: AsyncSession, user_id):
    result = await db.execute(
        select(models.UserBio).where(
            models.UserBio.user_id == user_id, models.UserBio.is_active == True
        )
    )
    return result.scalar_one_or_none()


async def update_user_bio(db: AsyncSession, bio_id, bio_text=None, is_active=None):
    result = await db.execute(
        select(models.UserBio).where(models.UserBio.bio_id == bio_id)
    )
    bio = result.scalar_one_or_none()
    if bio:
        if bio_text is not None:
            bio.bio_text = bio_text
        if is_active is not None:
            if is_active:
                others = await db.execute(
                    select(models.UserBio).where(
                        models.UserBio.user_id == bio.user_id,
                        models.UserBio.bio_id != bio_id,
                        models.UserBio.is_active == True,
                    )
                )
                for other in others.scalars().all():
                    other.is_active = False
            bio.is_active = is_active
        await db.commit()
        await db.refresh(bio)
    return bio


async def delete_user_bio(db: AsyncSession, bio_id):
    result = await db.execute(
        select(models.UserBio).where(models.UserBio.bio_id == bio_id)
    )
    bio = result.scalar_one_or_none()
    if bio:
        await db.delete(bio)
        await db.commit()
        return True
    return False


async def assign_role_to_user(db: AsyncSession, user_id, role_id):
    result = await db.execute(
        select(models.UserRole).where(
            models.UserRole.user_id == user_id, models.UserRole.role_id == role_id
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing
    new_ur = models.UserRole(
        user_id=user_id, role_id=role_id, created_at=datetime.utcnow()
    )
    db.add(new_ur)
    await db.commit()
    await db.refresh(new_ur)
    return new_ur


async def get_user_roles(db: AsyncSession, user_id):
    result = await db.execute(
        select(models.Role)
        .join(models.UserRole, models.Role.role_id == models.UserRole.role_id)
        .where(models.UserRole.user_id == user_id)
    )
    return list(result.scalars().all())


async def remove_role_from_user(db: AsyncSession, user_id, role_id):
    result = await db.execute(
        select(models.UserRole).where(
            models.UserRole.user_id == user_id, models.UserRole.role_id == role_id
        )
    )
    ur = result.scalar_one_or_none()
    if ur:
        await db.delete(ur)
        await db.commit()
        return True
    return False


async def create_privacy_history(
    db: AsyncSession, user_id, privacy_type, is_active=False
):
    if is_active:
        others = await db.execute(
            select(models.PrivacyHistory).where(
                models.PrivacyHistory.user_id == user_id,
                models.PrivacyHistory.privacy_type == privacy_type,
                models.PrivacyHistory.is_active == True,
            )
        )
        for other in others.scalars().all():
            other.is_active = False
    new_ph = models.PrivacyHistory(
        user_id=user_id,
        privacy_type=privacy_type,
        is_active=is_active,
        created_at=datetime.utcnow(),
    )
    db.add(new_ph)
    await db.commit()
    await db.refresh(new_ph)
    return new_ph


async def get_privacy_history_by_id(db: AsyncSession, privacy_id):
    result = await db.execute(
        select(models.PrivacyHistory).where(
            models.PrivacyHistory.privacy_id == privacy_id
        )
    )
    return result.scalar_one_or_none()


async def get_active_privacy_settings(db: AsyncSession, user_id):
    result = await db.execute(
        select(models.PrivacyHistory).where(
            models.PrivacyHistory.user_id == user_id,
            models.PrivacyHistory.is_active == True,
        )
    )
    return list(result.scalars().all())


async def update_privacy_setting(db: AsyncSession, privacy_id, is_active=None):
    result = await db.execute(
        select(models.PrivacyHistory).where(
            models.PrivacyHistory.privacy_id == privacy_id
        )
    )
    ph = result.scalar_one_or_none()
    if ph:
        if is_active is not None:
            if is_active:
                others = await db.execute(
                    select(models.PrivacyHistory).where(
                        models.PrivacyHistory.user_id == ph.user_id,
                        models.PrivacyHistory.privacy_type == ph.privacy_type,
                        models.PrivacyHistory.privacy_id != privacy_id,
                        models.PrivacyHistory.is_active == True,
                    )
                )
                for other in others.scalars().all():
                    other.is_active = False
            ph.is_active = is_active
        await db.commit()
        await db.refresh(ph)
    return ph


async def delete_privacy_history(db: AsyncSession, privacy_id):
    result = await db.execute(
        select(models.PrivacyHistory).where(
            models.PrivacyHistory.privacy_id == privacy_id
        )
    )
    ph = result.scalar_one_or_none()
    if ph:
        await db.delete(ph)
        await db.commit()
        return True
    return False


async def follow_user(db: AsyncSession, follower_id, following_id):
    existing = await db.execute(
        select(models.UserFollower).where(
            models.UserFollower.follower_id == follower_id,
            models.UserFollower.following_id == following_id,
        )
    )
    record = existing.scalar_one_or_none()
    if record:
        record.is_active = True
        await db.commit()
        await db.refresh(record)
        return record
    new_follow = models.UserFollower(
        follower_id=follower_id,
        following_id=following_id,
        is_active=True,
        created_at=datetime.utcnow(),
    )
    db.add(new_follow)
    await db.commit()
    await db.refresh(new_follow)
    return new_follow


async def unfollow_user(db: AsyncSession, follower_id, following_id):
    result = await db.execute(
        select(models.UserFollower).where(
            models.UserFollower.follower_id == follower_id,
            models.UserFollower.following_id == following_id,
        )
    )
    follow = result.scalar_one_or_none()
    if follow:
        follow.is_active = False
        await db.commit()
        await db.refresh(follow)
        return follow
    return None


async def get_followers(db: AsyncSession, user_id):
    result = await db.execute(
        select(models.User)
        .join(
            models.UserFollower, models.User.user_id == models.UserFollower.follower_id
        )
        .where(
            models.UserFollower.following_id == user_id,
            models.UserFollower.is_active == True,
        )
    )
    return list(result.scalars().all())


async def get_following(db: AsyncSession, user_id):
    result = await db.execute(
        select(models.User)
        .join(
            models.UserFollower, models.User.user_id == models.UserFollower.following_id
        )
        .where(
            models.UserFollower.follower_id == user_id,
            models.UserFollower.is_active == True,
        )
    )
    return list(result.scalars().all())


async def add_close_friend(db: AsyncSession, user_id, friend_id):
    result = await db.execute(
        select(models.CloseFriend).where(
            models.CloseFriend.user_id == user_id,
            models.CloseFriend.friend_id == friend_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing
    new_cf = models.CloseFriend(user_id=user_id, friend_id=friend_id)
    db.add(new_cf)
    await db.commit()
    await db.refresh(new_cf)
    return new_cf


async def get_close_friends(db: AsyncSession, user_id):
    result = await db.execute(
        select(models.User)
        .join(models.CloseFriend, models.User.user_id == models.CloseFriend.friend_id)
        .where(models.CloseFriend.user_id == user_id)
    )
    return list(result.scalars().all())


async def remove_close_friend(db: AsyncSession, user_id, friend_id):
    result = await db.execute(
        select(models.CloseFriend).where(
            models.CloseFriend.user_id == user_id,
            models.CloseFriend.friend_id == friend_id,
        )
    )
    cf = result.scalar_one_or_none()
    if cf:
        await db.delete(cf)
        await db.commit()
        return True
    return False


async def get_all_users(db: AsyncSession):
    result = await db.execute(select(models.User))
    return list(result.scalars().all())


async def search_users(db: AsyncSession, query: str, limit: int = 15):
    """Case-insensitive partial match on username and full_name."""
    pattern = f"%{query}%"
    result = await db.execute(
        select(models.User).where(
            models.User.username.ilike(pattern) | models.User.full_name.ilike(pattern)
        ).limit(limit)
    )
    return list(result.scalars().all())


async def create_refresh_token(
    db: AsyncSession, user_id: int, token_str: str, expires_delta_days: int = 7
):
    from datetime import datetime, timedelta

    expires_at = datetime.utcnow() + timedelta(days=expires_delta_days)
    new_token = models.RefreshToken(
        user_id=user_id, token=token_str, expires_at=expires_at, is_revoked=False
    )
    db.add(new_token)
    await db.commit()
    await db.refresh(new_token)
    return new_token


async def get_refresh_token_by_str(db: AsyncSession, token_str: str):
    result = await db.execute(
        select(models.RefreshToken).where(models.RefreshToken.token == token_str)
    )
    return result.scalar_one_or_none()


async def revoke_refresh_token(db: AsyncSession, token_str: str):
    token_obj = await get_refresh_token_by_str(db, token_str)
    if token_obj:
        token_obj.is_revoked = True
        await db.commit()
        await db.refresh(token_obj)
        return True
    return False


async def revoke_all_user_refresh_tokens(db: AsyncSession, user_id: int):
    from sqlalchemy import update

    await db.execute(
        update(models.RefreshToken)
        .where(
            models.RefreshToken.user_id == user_id,
            models.RefreshToken.is_revoked == False,
        )
        .values(is_revoked=True)
    )
    await db.commit()
