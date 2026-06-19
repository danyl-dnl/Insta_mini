from sqlalchemy import select, delete, func
from database import SessionLocal
from datetime import datetime, timedelta
import models


async def create_role(role_name):
    async with SessionLocal() as session:
        new_role = models.Role(role_name=role_name)
        session.add(new_role)
        await session.commit()
        await session.refresh(new_role)
        return new_role


async def get_role_by_id(role_id):
    async with SessionLocal() as session:
        result = await session.execute(select(models.Role).where(models.Role.role_id == role_id))
        return result.scalar_one_or_none()


async def get_role_by_name(role_name):
    async with SessionLocal() as session:
        result = await session.execute(select(models.Role).where(models.Role.role_name == role_name))
        return result.scalar_one_or_none()


async def update_role(role_id, new_role_name):
    async with SessionLocal() as session:
        result = await session.execute(select(models.Role).where(models.Role.role_id == role_id))
        role = result.scalar_one_or_none()
        if role:
            role.role_name = new_role_name
            await session.commit()
            await session.refresh(role)
        return role


async def delete_role(role_id):
    async with SessionLocal() as session:
        result = await session.execute(select(models.Role).where(models.Role.role_id == role_id))
        role = result.scalar_one_or_none()
        if role:
            await session.delete(role)
            await session.commit()
            return True
        return False


async def create_user(username, email, password, full_name=None, profile_picture=None):
    async with SessionLocal() as session:
        new_user = models.User(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            profile_picture=profile_picture,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user


async def get_user_by_id(user_id):
    async with SessionLocal() as session:
        result = await session.execute(select(models.User).where(models.User.user_id == user_id))
        return result.scalar_one_or_none()


async def get_user_by_username(username):
    async with SessionLocal() as session:
        result = await session.execute(select(models.User).where(models.User.username == username))
        return result.scalar_one_or_none()


async def get_user_by_email(email):
    async with SessionLocal() as session:
        result = await session.execute(select(models.User).where(models.User.email == email))
        return result.scalar_one_or_none()


async def update_user(user_id, full_name=None, profile_picture=None):
    async with SessionLocal() as session:
        result = await session.execute(select(models.User).where(models.User.user_id == user_id))
        user = result.scalar_one_or_none()
        if user:
            if full_name is not None:
                user.full_name = full_name
            if profile_picture is not None:
                user.profile_picture = profile_picture
            user.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(user)
        return user


async def delete_user(user_id):
    async with SessionLocal() as session:
        result = await session.execute(select(models.User).where(models.User.user_id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return False

        await session.execute(delete(models.CloseFriend).where(
            (models.CloseFriend.user_id == user_id) | (models.CloseFriend.friend_id == user_id)
        ))
        await session.execute(delete(models.PostLike).where(models.PostLike.user_id == user_id))
        await session.execute(delete(models.PostComment).where(models.PostComment.user_id == user_id))
        await session.execute(delete(models.SavedPost).where(models.SavedPost.user_id == user_id))
        await session.execute(delete(models.UserFollower).where(
            (models.UserFollower.follower_id == user_id) | (models.UserFollower.following_id == user_id)
        ))

        story_ids = list((await session.execute(
            select(models.Story.story_id).where(models.Story.user_id == user_id)
        )).scalars().all())
        if story_ids:
            await session.execute(delete(models.HighlightStory).where(
                models.HighlightStory.story_id.in_(story_ids)
            ))

        hl_ids = list((await session.execute(
            select(models.Highlight.highlight_id).where(models.Highlight.user_id == user_id)
        )).scalars().all())
        if hl_ids:
            await session.execute(delete(models.HighlightStory).where(
                models.HighlightStory.highlight_id.in_(hl_ids)
            ))

        await session.execute(delete(models.Highlight).where(models.Highlight.user_id == user_id))
        await session.execute(delete(models.Story).where(models.Story.user_id == user_id))

        post_ids = list((await session.execute(
            select(models.Post.post_id).where(models.Post.user_id == user_id)
        )).scalars().all())
        if post_ids:
            await session.execute(delete(models.SavedPost).where(models.SavedPost.post_id.in_(post_ids)))
            await session.execute(delete(models.PostLike).where(models.PostLike.post_id.in_(post_ids)))
            await session.execute(delete(models.PostComment).where(models.PostComment.post_id.in_(post_ids)))

        await session.execute(delete(models.Post).where(models.Post.user_id == user_id))
        await session.execute(delete(models.PrivacyHistory).where(models.PrivacyHistory.user_id == user_id))
        await session.execute(delete(models.UserRole).where(models.UserRole.user_id == user_id))
        await session.execute(delete(models.UserBio).where(models.UserBio.user_id == user_id))
        await session.delete(user)
        await session.commit()
        return True


async def create_user_bio(user_id, bio_text, is_active=False):
    async with SessionLocal() as session:
        if is_active:
            others = await session.execute(
                select(models.UserBio).where(models.UserBio.user_id == user_id, models.UserBio.is_active == True)
            )
            for other in others.scalars().all():
                other.is_active = False
        new_bio = models.UserBio(user_id=user_id, bio_text=bio_text, is_active=is_active)
        session.add(new_bio)
        await session.commit()
        await session.refresh(new_bio)
        return new_bio


async def get_user_bio_by_id(bio_id):
    async with SessionLocal() as session:
        result = await session.execute(select(models.UserBio).where(models.UserBio.bio_id == bio_id))
        return result.scalar_one_or_none()


async def get_active_user_bio(user_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.UserBio).where(models.UserBio.user_id == user_id, models.UserBio.is_active == True)
        )
        return result.scalar_one_or_none()


async def update_user_bio(bio_id, bio_text=None, is_active=None):
    async with SessionLocal() as session:
        result = await session.execute(select(models.UserBio).where(models.UserBio.bio_id == bio_id))
        bio = result.scalar_one_or_none()
        if bio:
            if bio_text is not None:
                bio.bio_text = bio_text
            if is_active is not None:
                if is_active:
                    others = await session.execute(
                        select(models.UserBio).where(
                            models.UserBio.user_id == bio.user_id,
                            models.UserBio.bio_id != bio_id,
                            models.UserBio.is_active == True
                        )
                    )
                    for other in others.scalars().all():
                        other.is_active = False
                bio.is_active = is_active
            await session.commit()
            await session.refresh(bio)
        return bio


async def delete_user_bio(bio_id):
    async with SessionLocal() as session:
        result = await session.execute(select(models.UserBio).where(models.UserBio.bio_id == bio_id))
        bio = result.scalar_one_or_none()
        if bio:
            await session.delete(bio)
            await session.commit()
            return True
        return False


async def assign_role_to_user(user_id, role_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.UserRole).where(
                models.UserRole.user_id == user_id,
                models.UserRole.role_id == role_id
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing
        new_ur = models.UserRole(user_id=user_id, role_id=role_id, created_at=datetime.utcnow())
        session.add(new_ur)
        await session.commit()
        await session.refresh(new_ur)
        return new_ur


async def get_user_roles(user_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.Role)
            .join(models.UserRole, models.Role.role_id == models.UserRole.role_id)
            .where(models.UserRole.user_id == user_id)
        )
        return list(result.scalars().all())


async def remove_role_from_user(user_id, role_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.UserRole).where(
                models.UserRole.user_id == user_id,
                models.UserRole.role_id == role_id
            )
        )
        ur = result.scalar_one_or_none()
        if ur:
            await session.delete(ur)
            await session.commit()
            return True
        return False


async def create_privacy_history(user_id, privacy_type, is_active=False):
    async with SessionLocal() as session:
        if is_active:
            others = await session.execute(
                select(models.PrivacyHistory).where(
                    models.PrivacyHistory.user_id == user_id,
                    models.PrivacyHistory.privacy_type == privacy_type,
                    models.PrivacyHistory.is_active == True
                )
            )
            for other in others.scalars().all():
                other.is_active = False
        new_ph = models.PrivacyHistory(
            user_id=user_id,
            privacy_type=privacy_type,
            is_active=is_active,
            created_at=datetime.utcnow()
        )
        session.add(new_ph)
        await session.commit()
        await session.refresh(new_ph)
        return new_ph


async def get_privacy_history_by_id(privacy_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.PrivacyHistory).where(models.PrivacyHistory.privacy_id == privacy_id)
        )
        return result.scalar_one_or_none()


async def get_active_privacy_settings(user_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.PrivacyHistory).where(
                models.PrivacyHistory.user_id == user_id,
                models.PrivacyHistory.is_active == True
            )
        )
        return list(result.scalars().all())


async def update_privacy_setting(privacy_id, is_active=None):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.PrivacyHistory).where(models.PrivacyHistory.privacy_id == privacy_id)
        )
        ph = result.scalar_one_or_none()
        if ph:
            if is_active is not None:
                if is_active:
                    others = await session.execute(
                        select(models.PrivacyHistory).where(
                            models.PrivacyHistory.user_id == ph.user_id,
                            models.PrivacyHistory.privacy_type == ph.privacy_type,
                            models.PrivacyHistory.privacy_id != privacy_id,
                            models.PrivacyHistory.is_active == True
                        )
                    )
                    for other in others.scalars().all():
                        other.is_active = False
                ph.is_active = is_active
            await session.commit()
            await session.refresh(ph)
        return ph


async def delete_privacy_history(privacy_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.PrivacyHistory).where(models.PrivacyHistory.privacy_id == privacy_id)
        )
        ph = result.scalar_one_or_none()
        if ph:
            await session.delete(ph)
            await session.commit()
            return True
        return False


async def create_post(user_id, caption, image_url):
    async with SessionLocal() as session:
        new_post = models.Post(
            user_id=user_id,
            caption=caption,
            image_url=image_url,
            created_at=datetime.utcnow(),
        )
        session.add(new_post)
        await session.commit()
        await session.refresh(new_post)
        return new_post


async def get_post_by_id(post_id):
    async with SessionLocal() as session:
        result = await session.execute(select(models.Post).where(models.Post.post_id == post_id))
        return result.scalar_one_or_none()


async def get_posts_by_user(user_id):
    async with SessionLocal() as session:
        result = await session.execute(select(models.User).where(models.User.user_id == user_id))
        user = result.scalar_one_or_none()
        return user.posts if user else []


async def update_post_caption(post_id, new_caption):
    async with SessionLocal() as session:
        result = await session.execute(select(models.Post).where(models.Post.post_id == post_id))
        post = result.scalar_one_or_none()
        if post:
            post.caption = new_caption
            await session.commit()
            await session.refresh(post)
        return post


async def update_post(post_id, caption):
    return await update_post_caption(post_id, caption)


async def delete_post(post_id):
    async with SessionLocal() as session:
        result = await session.execute(select(models.Post).where(models.Post.post_id == post_id))
        post = result.scalar_one_or_none()
        if post:
            await session.execute(delete(models.SavedPost).where(models.SavedPost.post_id == post_id))
            await session.execute(delete(models.PostLike).where(models.PostLike.post_id == post_id))
            await session.execute(delete(models.PostComment).where(models.PostComment.post_id == post_id))
            await session.delete(post)
            await session.commit()
            return True
        return False


async def follow_user(follower_id, following_id):
    async with SessionLocal() as session:
        existing = await session.execute(
            select(models.UserFollower).where(
                models.UserFollower.follower_id == follower_id,
                models.UserFollower.following_id == following_id,
            )
        )
        record = existing.scalar_one_or_none()
        if record:
            record.is_active = True
            await session.commit()
            await session.refresh(record)
            return record
        new_follow = models.UserFollower(
            follower_id=follower_id,
            following_id=following_id,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        session.add(new_follow)
        await session.commit()
        await session.refresh(new_follow)
        return new_follow


async def unfollow_user(follower_id, following_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.UserFollower).where(
                models.UserFollower.follower_id == follower_id,
                models.UserFollower.following_id == following_id,
            )
        )
        follow = result.scalar_one_or_none()
        if follow:
            follow.is_active = False
            await session.commit()
            await session.refresh(follow)
            return follow
        return None


async def get_followers(user_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.User)
            .join(models.UserFollower, models.User.user_id == models.UserFollower.follower_id)
            .where(
                models.UserFollower.following_id == user_id,
                models.UserFollower.is_active == True,
            )
        )
        return list(result.scalars().all())


async def get_following(user_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.User)
            .join(models.UserFollower, models.User.user_id == models.UserFollower.following_id)
            .where(
                models.UserFollower.follower_id == user_id,
                models.UserFollower.is_active == True,
            )
        )
        return list(result.scalars().all())


async def create_story(user_id, media_url, created_at=None, expires_at=None):
    async with SessionLocal() as session:
        now = datetime.utcnow()
        new_story = models.Story(
            user_id=user_id,
            media_url=media_url,
            created_at=created_at if created_at is not None else now,
            expires_at=expires_at if expires_at is not None else (now + timedelta(days=1)),
        )
        session.add(new_story)
        await session.commit()
        await session.refresh(new_story)
        return new_story


async def get_story_by_id(story_id):
    async with SessionLocal() as session:
        result = await session.execute(select(models.Story).where(models.Story.story_id == story_id))
        return result.scalar_one_or_none()


async def get_active_stories_by_user(user_id):
    async with SessionLocal() as session:
        result = await session.execute(select(models.User).where(models.User.user_id == user_id))
        user = result.scalar_one_or_none()
        if user:
            now = datetime.utcnow()
            return [s for s in user.stories if s.expires_at > now]
        return []

get_active_stories = get_active_stories_by_user


async def delete_story(story_id):
    async with SessionLocal() as session:
        result = await session.execute(select(models.Story).where(models.Story.story_id == story_id))
        story = result.scalar_one_or_none()
        if story:
            await session.execute(delete(models.HighlightStory).where(
                models.HighlightStory.story_id == story_id
            ))
            await session.delete(story)
            await session.commit()
            return True
        return False


async def save_post(user_id, post_id):
    async with SessionLocal() as session:
        existing = await session.execute(
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
        session.add(new_save)
        await session.commit()
        await session.refresh(new_save)
        return new_save


async def unsave_post(user_id, post_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.SavedPost).where(
                models.SavedPost.user_id == user_id,
                models.SavedPost.post_id == post_id,
            )
        )
        saved = result.scalar_one_or_none()
        if saved:
            await session.delete(saved)
            await session.commit()
            return True
        return False


async def get_saved_posts(user_id):
    async with SessionLocal() as session:
        result = await session.execute(select(models.User).where(models.User.user_id == user_id))
        user = result.scalar_one_or_none()
        return [sp.post for sp in user.saved_posts] if user else []


async def create_highlight(user_id, title, cover_url=None):
    async with SessionLocal() as session:
        new_hl = models.Highlight(
            user_id=user_id,
            title=title,
            cover_url=cover_url,
            created_at=datetime.utcnow()
        )
        session.add(new_hl)
        await session.commit()
        await session.refresh(new_hl)
        return new_hl


async def get_highlight_by_id(highlight_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.Highlight).where(models.Highlight.highlight_id == highlight_id)
        )
        return result.scalar_one_or_none()


async def get_highlights_by_user(user_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.Highlight).where(models.Highlight.user_id == user_id)
        )
        return list(result.scalars().all())


async def update_highlight(highlight_id, title=None, cover_url=None):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.Highlight).where(models.Highlight.highlight_id == highlight_id)
        )
        hl = result.scalar_one_or_none()
        if hl:
            if title is not None:
                hl.title = title
            if cover_url is not None:
                hl.cover_url = cover_url
            await session.commit()
            await session.refresh(hl)
        return hl


async def delete_highlight(highlight_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.Highlight).where(models.Highlight.highlight_id == highlight_id)
        )
        hl = result.scalar_one_or_none()
        if hl:
            await session.execute(
                delete(models.HighlightStory).where(models.HighlightStory.highlight_id == highlight_id)
            )
            await session.execute(
                delete(models.Highlight).where(models.Highlight.highlight_id == highlight_id)
            )
            await session.commit()
            return True
        return False


async def add_story_to_highlight(highlight_id, story_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.HighlightStory).where(
                models.HighlightStory.highlight_id == highlight_id,
                models.HighlightStory.story_id == story_id
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing
        new_hls = models.HighlightStory(highlight_id=highlight_id, story_id=story_id)
        session.add(new_hls)
        await session.commit()
        await session.refresh(new_hls)
        return new_hls


async def get_stories_in_highlight(highlight_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.Story)
            .join(models.HighlightStory, models.Story.story_id == models.HighlightStory.story_id)
            .where(models.HighlightStory.highlight_id == highlight_id)
        )
        return list(result.scalars().all())


async def remove_story_from_highlight(highlight_id, story_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.HighlightStory).where(
                models.HighlightStory.highlight_id == highlight_id,
                models.HighlightStory.story_id == story_id
            )
        )
        hls = result.scalar_one_or_none()
        if hls:
            await session.delete(hls)
            await session.commit()
            return True
        return False


async def add_close_friend(user_id, friend_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.CloseFriend).where(
                models.CloseFriend.user_id == user_id,
                models.CloseFriend.friend_id == friend_id
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing
        new_cf = models.CloseFriend(user_id=user_id, friend_id=friend_id)
        session.add(new_cf)
        await session.commit()
        await session.refresh(new_cf)
        return new_cf


async def get_close_friends(user_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.User)
            .join(models.CloseFriend, models.User.user_id == models.CloseFriend.friend_id)
            .where(models.CloseFriend.user_id == user_id)
        )
        return list(result.scalars().all())


async def remove_close_friend(user_id, friend_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.CloseFriend).where(
                models.CloseFriend.user_id == user_id,
                models.CloseFriend.friend_id == friend_id
            )
        )
        cf = result.scalar_one_or_none()
        if cf:
            await session.delete(cf)
            await session.commit()
            return True
        return False


async def like_post(user_id, post_id):
    async with SessionLocal() as session:
        existing = await session.execute(
            select(models.PostLike).where(
                models.PostLike.user_id == user_id,
                models.PostLike.post_id == post_id,
            )
        )
        like = existing.scalar_one_or_none()
        if like:
            return like
        new_like = models.PostLike(user_id=user_id, post_id=post_id)
        session.add(new_like)
        await session.commit()
        await session.refresh(new_like)
        return new_like


async def unlike_post(user_id, post_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.PostLike).where(
                models.PostLike.user_id == user_id,
                models.PostLike.post_id == post_id,
            )
        )
        like = result.scalar_one_or_none()
        if like:
            await session.delete(like)
            await session.commit()
            return True
        return False


async def get_likes_count(post_id):
    async with SessionLocal() as session:
        result = await session.execute(select(models.Post).where(models.Post.post_id == post_id))
        post = result.scalar_one_or_none()
        return len(post.likes) if post else 0

get_post_likes_count = get_likes_count


async def get_users_who_liked_post(post_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.User)
            .join(models.PostLike, models.User.user_id == models.PostLike.user_id)
            .where(models.PostLike.post_id == post_id)
        )
        return list(result.scalars().all())


async def add_comment(user_id, post_id, comment_text):
    async with SessionLocal() as session:
        new_comment = models.PostComment(
            user_id=user_id,
            post_id=post_id,
            comment_text=comment_text,
        )
        session.add(new_comment)
        await session.commit()
        await session.refresh(new_comment)
        return new_comment


async def get_comments_for_post(post_id):
    async with SessionLocal() as session:
        result = await session.execute(select(models.Post).where(models.Post.post_id == post_id))
        post = result.scalar_one_or_none()
        return post.comments if post else []


async def get_comment_by_id(comment_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.PostComment).where(models.PostComment.comment_id == comment_id)
        )
        return result.scalar_one_or_none()


async def update_comment(comment_id, comment_text):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.PostComment).where(models.PostComment.comment_id == comment_id)
        )
        comment = result.scalar_one_or_none()
        if comment:
            comment.comment_text = comment_text
            await session.commit()
            await session.refresh(comment)
        return comment


async def delete_comment(comment_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.PostComment).where(models.PostComment.comment_id == comment_id)
        )
        comment = result.scalar_one_or_none()
        if comment:
            await session.delete(comment)
            await session.commit()
            return True
        return False


async def get_all_users():
    async with SessionLocal() as session:
        result = await session.execute(select(models.User))
        return list(result.scalars().all())


async def get_all_posts():
    async with SessionLocal() as session:
        result = await session.execute(select(models.Post).order_by(models.Post.created_at.desc()))
        return list(result.scalars().all())

