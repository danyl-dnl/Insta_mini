from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import os
import shutil
import uuid
from Setting.Database import get_db
from Setting.Security import verify_password, create_access_token, decode_access_token, generate_refresh_token_string
from Setting.Mongo import get_mongo_db
from pymongo.errors import DuplicateKeyError
import User.Schemas.token as token_schemas
import User.CRUD.user as user_crud
import User.CRUD.post as post_crud
import User.CRUD.story as story_crud
import User.CRUD.reel as reel_crud
import User.Schemas.user as user_schemas
import User.Schemas.post as post_schemas
import User.Schemas.story as story_schemas
import User.Schemas.reel as reel_schemas
from Setting.Models import Role, UserRole, User
from sqlalchemy import select

UserRouter = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login", auto_error=False)


async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = await user_crud.get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user


UserProtectedRouter = APIRouter(dependencies=[Depends(get_current_user)])


def role_to_dict(role):
    if not role:
        return None
    return {
        "role_id": role.role_id,
        "role_name": role.role_name
    }


def user_to_dict(user):
    if not user:
        return None
    return {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "profile_picture": user.profile_picture,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }


def bio_to_dict(bio):
    if not bio:
        return None
    return {
        "bio_id": bio.bio_id,
        "user_id": bio.user_id,
        "bio_text": bio.bio_text,
        "is_active": bio.is_active,
        "created_at": bio.created_at.isoformat() if bio.created_at else None,
    }


def privacy_to_dict(ph):
    if not ph:
        return None
    return {
        "privacy_id": ph.privacy_id,
        "user_id": ph.user_id,
        "privacy_type": ph.privacy_type,
        "is_active": ph.is_active,
        "created_at": ph.created_at.isoformat() if ph.created_at else None,
    }


def post_to_dict(post):
    if not post:
        return None
    return {
        "post_id": post.post_id,
        "user_id": post.user_id,
        "caption": post.caption,
        "image_url": post.image_url,
        "created_at": post.created_at.isoformat() if post.created_at else None,
    }


def like_to_dict(like):
    if not like:
        return None
    return {
        "like_id": like.like_id,
        "user_id": like.user_id,
        "post_id": like.post_id,
        "created_at": like.created_at.isoformat() if like.created_at else None,
    }


def comment_to_dict(comment):
    if not comment:
        return None
    return {
        "comment_id": comment.comment_id,
        "user_id": comment.user_id,
        "post_id": comment.post_id,
        "comment_text": comment.comment_text,
        "created_at": comment.created_at.isoformat() if comment.created_at else None,
    }


def story_to_dict(story):
    if not story:
        return None
    return {
        "story_id": story.story_id,
        "user_id": story.user_id,
        "media_url": story.media_url,
        "created_at": story.created_at.isoformat() if story.created_at else None,
        "expires_at": story.expires_at.isoformat() if story.expires_at else None,
    }


def highlight_to_dict(hl):
    if not hl:
        return None
    return {
        "highlight_id": hl.highlight_id,
        "user_id": hl.user_id,
        "title": hl.title,
        "cover_url": hl.cover_url,
        "created_at": hl.created_at.isoformat() if hl.created_at else None,
    }


def reel_to_dict(reel):
    if not reel:
        return None
    return {
        "reel_id": reel.reel_id,
        "user_id": reel.user_id,
        "video_url": reel.video_url,
        "caption": reel.caption,
        "created_at": reel.created_at.isoformat() if reel.created_at else None,
    }


@UserRouter.post("/login")
async def login(login_data: user_schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_user_by_username(db, login_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    refresh_token_str = generate_refresh_token_string()
    await user_crud.create_refresh_token(db, user.user_id, refresh_token_str)
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token_str, 
        "token_type": "bearer"
    }


@UserRouter.post("/refresh")
async def refresh_token_endpoint(refresh_data: token_schemas.RefreshRequest, db: AsyncSession = Depends(get_db)):
    token_obj = await user_crud.get_refresh_token_by_str(db, refresh_data.refresh_token)
    if not token_obj:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if token_obj.is_revoked:
        await user_crud.revoke_all_user_refresh_tokens(db, token_obj.user_id)
        raise HTTPException(status_code=401, detail="Refresh token has been revoked. All sessions invalidated.")
    
    from datetime import datetime
    if token_obj.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token has expired")
    
    token_obj.is_revoked = True
    new_refresh_str = generate_refresh_token_string()
    await user_crud.create_refresh_token(db, token_obj.user_id, new_refresh_str)
    
    user = await user_crud.get_user_by_id(db, token_obj.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    new_access_token = create_access_token(data={"sub": user.username})
    
    await db.commit()
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_str,
        "token_type": "bearer"
    }


@UserProtectedRouter.post("/logout")
async def logout_endpoint(refresh_data: token_schemas.RefreshRequest, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    await user_crud.revoke_refresh_token(db, refresh_data.refresh_token)
    return {"message": "Session logged out successfully"}


@UserProtectedRouter.get("/users/me")
async def get_me(current_user = Depends(get_current_user)):
    return user_to_dict(current_user)


@UserProtectedRouter.get("/users")
async def get_all_users(db: AsyncSession = Depends(get_db)):
    users = await user_crud.get_all_users(db)
    return [user_to_dict(u) for u in users]


@UserProtectedRouter.get("/posts")
async def get_all_posts(db: AsyncSession = Depends(get_db)):
    posts = await post_crud.get_all_posts(db)
    return [post_to_dict(p) for p in posts]


@UserRouter.post("/users", status_code=201)
async def create_user(user_data: user_schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    existing_username = await user_crud.get_user_by_username(db, user_data.username)
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    existing_email = await user_crud.get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = await user_crud.create_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        profile_picture=user_data.profile_picture
    )
    return user_to_dict(user)


@UserProtectedRouter.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_to_dict(user)


@UserProtectedRouter.get("/users/username/{username}")
async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_to_dict(user)


@UserProtectedRouter.get("/users/email/{email}")
async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_to_dict(user)


@UserProtectedRouter.put("/users/{user_id}")
async def update_user(user_id: int, user_data: user_schemas.UserUpdate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")
    user = await user_crud.update_user(
        db=db,
        user_id=user_id,
        full_name=user_data.full_name,
        profile_picture=user_data.profile_picture
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_to_dict(user)


@UserProtectedRouter.post("/users/{user_id}/bio", status_code=201)
async def create_user_bio(user_id: int, bio_data: user_schemas.UserBioCreate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to create a bio for this user")
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    bio = await user_crud.create_user_bio(db, user_id, bio_data.bio_text, bio_data.is_active)
    return bio_to_dict(bio)


@UserProtectedRouter.get("/users/{user_id}/bio")
async def get_active_bio(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    bio = await user_crud.get_active_user_bio(db, user_id)
    if not bio:
        raise HTTPException(status_code=404, detail="Active bio not found for user")
    return bio_to_dict(bio)


@UserProtectedRouter.put("/bios/{bio_id}")
async def update_bio(bio_id: int, bio_data: user_schemas.UserBioUpdate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    bio_record = await user_crud.get_user_bio_by_id(db, bio_id)
    if not bio_record:
        raise HTTPException(status_code=404, detail="Bio not found")
    if bio_record.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this bio")
    bio = await user_crud.update_user_bio(db, bio_id, bio_data.bio_text, bio_data.is_active)
    if not bio:
        raise HTTPException(status_code=404, detail="Bio not found")
    return bio_to_dict(bio)


@UserProtectedRouter.delete("/bios/{bio_id}")
async def delete_bio(bio_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    bio_record = await user_crud.get_user_bio_by_id(db, bio_id)
    if not bio_record:
        raise HTTPException(status_code=404, detail="Bio not found")
    if bio_record.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this bio")
    deleted = await user_crud.delete_user_bio(db, bio_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Bio not found")
    return {"message": "Bio deleted successfully"}


@UserProtectedRouter.post("/users/{user_id}/roles/{role_id}", status_code=201)
async def assign_role_to_user(user_id: int, role_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    # Check if current_user is Admin
    admin_check = await db.execute(
        select(Role)
        .join(UserRole, Role.role_id == UserRole.role_id)
        .where(UserRole.user_id == current_user.user_id, Role.role_name == "Admin")
    )
    if not admin_check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Only administrators can assign roles")
    
    import Admin.CRUD.role as role_crud
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    role = await role_crud.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    await user_crud.assign_role_to_user(db, user_id, role_id)
    return {"message": "Role assigned successfully"}


@UserProtectedRouter.get("/users/{user_id}/roles")
async def get_user_roles(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    roles = await user_crud.get_user_roles(db, user_id)
    return [role_to_dict(r) for r in roles]


@UserProtectedRouter.delete("/users/{user_id}/roles/{role_id}")
async def remove_role_from_user(user_id: int, role_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    # Check if current_user is Admin
    admin_check = await db.execute(
        select(Role)
        .join(UserRole, Role.role_id == UserRole.role_id)
        .where(UserRole.user_id == current_user.user_id, Role.role_name == "Admin")
    )
    if not admin_check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Only administrators can remove roles")

    removed = await user_crud.remove_role_from_user(db, user_id, role_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Role assignment not found")
    return {"message": "Role removed successfully"}


@UserProtectedRouter.post("/users/{user_id}/privacy", status_code=201)
async def create_privacy_setting(user_id: int, privacy_data: user_schemas.PrivacyHistoryCreate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to create privacy settings for this user")
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    ph = await user_crud.create_privacy_history(db, user_id, privacy_data.privacy_type, privacy_data.is_active)
    return privacy_to_dict(ph)


@UserProtectedRouter.get("/users/{user_id}/privacy")
async def get_active_privacy(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    settings = await user_crud.get_active_privacy_settings(db, user_id)
    return [privacy_to_dict(ph) for ph in settings]


@UserProtectedRouter.put("/privacy/{privacy_id}")
async def update_privacy(privacy_id: int, privacy_data: user_schemas.PrivacyHistoryUpdate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    ph = await user_crud.get_privacy_history_by_id(db, privacy_id)
    if not ph:
        raise HTTPException(status_code=404, detail="Privacy record not found")
    if ph.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this privacy setting")
    ph = await user_crud.update_privacy_setting(db, privacy_id, privacy_data.is_active)
    return privacy_to_dict(ph)


@UserProtectedRouter.delete("/privacy/{privacy_id}")
async def delete_privacy(privacy_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    ph = await user_crud.get_privacy_history_by_id(db, privacy_id)
    if not ph:
        raise HTTPException(status_code=404, detail="Privacy record not found")
    if ph.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this privacy setting")
    deleted = await user_crud.delete_privacy_history(db, privacy_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Privacy record not found")
    return {"message": "Privacy record deleted successfully"}


@UserProtectedRouter.post("/users/{follower_id}/follow/{following_id}", status_code=201)
async def follow_user(follower_id: int, following_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.user_id != follower_id:
        raise HTTPException(status_code=403, detail="Not authorized to perform follow on behalf of other users")
    if follower_id == following_id:
        raise HTTPException(status_code=400, detail="Users cannot follow themselves")
    follower = await user_crud.get_user_by_id(db, follower_id)
    following = await user_crud.get_user_by_id(db, following_id)
    if not follower or not following:
        raise HTTPException(status_code=404, detail="Follower or following user not found")
    record = await user_crud.follow_user(db, follower_id, following_id)
    return {
        "follow_id": record.follow_id,
        "follower_id": record.follower_id,
        "following_id": record.following_id,
        "is_active": record.is_active,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }


@UserProtectedRouter.post("/users/{follower_id}/unfollow/{following_id}")
async def unfollow_user(follower_id: int, following_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.user_id != follower_id:
        raise HTTPException(status_code=403, detail="Not authorized to perform unfollow on behalf of other users")
    unfollowed = await user_crud.unfollow_user(db, follower_id, following_id)
    if not unfollowed:
        raise HTTPException(status_code=404, detail="Follow relationship not found")
    return {
        "follow_id": unfollowed.follow_id,
        "follower_id": unfollowed.follower_id,
        "following_id": unfollowed.following_id,
        "is_active": unfollowed.is_active,
        "created_at": unfollowed.created_at.isoformat() if unfollowed.created_at else None,
    }


@UserProtectedRouter.get("/users/{user_id}/followers")
async def get_followers(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    followers = await user_crud.get_followers(db, user_id)
    return [user_to_dict(f) for f in followers]


@UserProtectedRouter.get("/users/{user_id}/following")
async def get_following(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    following = await user_crud.get_following(db, user_id)
    return [user_to_dict(f) for f in following]


@UserProtectedRouter.post("/users/{user_id}/close-friends/{friend_id}", status_code=201)
async def add_close_friend(user_id: int, friend_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to manage close friends for other users")
    if user_id == friend_id:
        raise HTTPException(status_code=400, detail="Cannot add yourself as close friend")
    user = await user_crud.get_user_by_id(db, user_id)
    friend = await user_crud.get_user_by_id(db, friend_id)
    if not user or not friend:
        raise HTTPException(status_code=404, detail="User or Friend not found")
    await user_crud.add_close_friend(db, user_id, friend_id)
    return {"message": "Added to close friends successfully"}


@UserProtectedRouter.delete("/users/{user_id}/close-friends/{friend_id}")
async def remove_close_friend(user_id: int, friend_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to manage close friends for other users")
    removed = await user_crud.remove_close_friend(db, user_id, friend_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Close friend relationship not found")
    return {"message": "Removed from close friends successfully"}


@UserProtectedRouter.get("/users/{user_id}/close-friends")
async def get_close_friends(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    friends = await user_crud.get_close_friends(db, user_id)
    return [user_to_dict(f) for f in friends]


@UserProtectedRouter.post("/posts", status_code=201)
async def create_post(post_data: post_schemas.PostCreate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.user_id != post_data.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to create posts for other users")
    user = await user_crud.get_user_by_id(db, post_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    post = await post_crud.create_post(db, post_data.user_id, post_data.caption, post_data.image_url)
    return post_to_dict(post)


@UserProtectedRouter.get("/posts/{post_id}")
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await post_crud.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post_to_dict(post)


@UserProtectedRouter.get("/users/{user_id}/posts")
async def get_user_posts(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    posts = await post_crud.get_posts_by_user(db, user_id)
    return [post_to_dict(p) for p in posts]


@UserProtectedRouter.put("/posts/{post_id}")
async def update_post(post_id: int, post_data: post_schemas.PostUpdate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    post = await post_crud.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    post = await post_crud.update_post(db, post_id, post_data.caption)
    return post_to_dict(post)


@UserProtectedRouter.post("/users/{user_id}/save/{post_id}", status_code=201)
async def save_post(user_id: int, post_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to save posts for other users")
    user = await user_crud.get_user_by_id(db, user_id)
    post = await post_crud.get_post_by_id(db, post_id)
    if not user or not post:
        raise HTTPException(status_code=404, detail="User or Post not found")
    record = await post_crud.save_post(db, user_id, post_id)
    if not record:
        return {"message": "Post already saved"}
    return {"message": "Post saved successfully"}


@UserProtectedRouter.delete("/users/{user_id}/unsave/{post_id}")
async def unsave_post(user_id: int, post_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to unsave posts for other users")
    deleted = await post_crud.unsave_post(db, user_id, post_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Saved post record not found")
    return {"message": "Post unsaved successfully"}


@UserProtectedRouter.get("/users/{user_id}/saved")
async def get_saved_posts(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    posts = await post_crud.get_saved_posts(db, user_id)
    return [post_to_dict(p) for p in posts]


@UserProtectedRouter.post("/posts/{post_id}/like", status_code=201)
async def like_post(post_id: int, like_data: post_schemas.PostLikeCreate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.user_id != like_data.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to like posts on behalf of other users")
    post = await post_crud.get_post_by_id(db, post_id)
    user = await user_crud.get_user_by_id(db, like_data.user_id)
    if not post or not user:
        raise HTTPException(status_code=404, detail="Post or User not found")
    like = await post_crud.like_post(db, like_data.user_id, post_id)
    return like_to_dict(like)


@UserProtectedRouter.delete("/posts/{post_id}/like/{user_id}")
async def unlike_post(post_id: int, user_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to unlike posts on behalf of other users")
    unliked = await post_crud.unlike_post(db, user_id, post_id)
    if not unliked:
        raise HTTPException(status_code=404, detail="Like record not found")
    return {"message": "Post unliked successfully"}


@UserProtectedRouter.get("/posts/{post_id}/likes/count")
async def get_post_likes_count(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await post_crud.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    count = await post_crud.get_post_likes_count(db, post_id)
    return {"likes_count": count}


@UserProtectedRouter.get("/posts/{post_id}/likes/users")
async def get_users_who_liked_post(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await post_crud.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    users = await post_crud.get_users_who_liked_post(db, post_id)
    return [user_to_dict(u) for u in users]


@UserProtectedRouter.post("/posts/{post_id}/comments", status_code=201)
async def add_comment(post_id: int, comment_data: post_schemas.CommentCreate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.user_id != comment_data.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to comment on behalf of other users")
    post = await post_crud.get_post_by_id(db, post_id)
    user = await user_crud.get_user_by_id(db, comment_data.user_id)
    if not post or not user:
        raise HTTPException(status_code=404, detail="Post or User not found")
    comment = await post_crud.add_comment(db, comment_data.user_id, post_id, comment_data.comment_text)
    return comment_to_dict(comment)


@UserProtectedRouter.get("/posts/{post_id}/comments")
async def get_comments_for_post(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await post_crud.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comments = await post_crud.get_comments_for_post(db, post_id)
    return [comment_to_dict(c) for c in comments]


@UserProtectedRouter.get("/comments/{comment_id}")
async def get_comment(comment_id: int, db: AsyncSession = Depends(get_db)):
    comment = await post_crud.get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment_to_dict(comment)


@UserProtectedRouter.put("/comments/{comment_id}")
async def update_comment(comment_id: int, comment_data: post_schemas.CommentUpdate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    comment = await post_crud.get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")
    comment = await post_crud.update_comment(db, comment_id, comment_data.comment_text)
    return comment_to_dict(comment)


@UserProtectedRouter.delete("/comments/{comment_id}")
async def delete_comment(comment_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    comment = await post_crud.get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    post = await post_crud.get_post_by_id(db, comment.post_id)
    # Allow deletion by comment author, post owner, or admin
    admin_check = await db.execute(
        select(Role)
        .join(UserRole, Role.role_id == UserRole.role_id)
        .where(UserRole.user_id == current_user.user_id, Role.role_name == "Admin")
    )
    is_admin = admin_check.scalar_one_or_none() is not None
    if comment.user_id != current_user.user_id and (not post or post.user_id != current_user.user_id) and not is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    deleted = await post_crud.delete_comment(db, comment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"message": "Comment deleted successfully"}


@UserProtectedRouter.post("/stories", status_code=201)
async def create_story(story_data: story_schemas.StoryCreate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.user_id != story_data.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to create stories for other users")
    user = await user_crud.get_user_by_id(db, story_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    story = await story_crud.create_story(db, story_data.user_id, story_data.media_url)
    return story_to_dict(story)


@UserProtectedRouter.get("/users/{user_id}/stories/active")
async def get_active_stories(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    stories = await story_crud.get_active_stories_by_user(db, user_id)
    return [story_to_dict(s) for s in stories]


@UserProtectedRouter.delete("/stories/{story_id}")
async def delete_story(story_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    story = await story_crud.get_story_by_id(db, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    if story.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this story")
    deleted = await story_crud.delete_story(db, story_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Story not found")
    return {"message": "Story deleted successfully"}


@UserProtectedRouter.post("/highlights", status_code=201)
async def create_highlight(hl_data: story_schemas.HighlightCreate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.user_id != hl_data.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to create highlights for other users")
    user = await user_crud.get_user_by_id(db, hl_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    hl = await story_crud.create_highlight(db, hl_data.user_id, hl_data.title, hl_data.cover_url)
    return highlight_to_dict(hl)


@UserProtectedRouter.get("/highlights/{highlight_id}")
async def get_highlight(highlight_id: int, db: AsyncSession = Depends(get_db)):
    hl = await story_crud.get_highlight_by_id(db, highlight_id)
    if not hl:
        raise HTTPException(status_code=404, detail="Highlight not found")
    return highlight_to_dict(hl)


@UserProtectedRouter.get("/users/{user_id}/highlights")
async def get_user_highlights(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    hls = await story_crud.get_highlights_by_user(db, user_id)
    return [highlight_to_dict(hl) for hl in hls]


@UserProtectedRouter.put("/highlights/{highlight_id}")
async def update_highlight(highlight_id: int, hl_data: story_schemas.HighlightUpdate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    hl = await story_crud.get_highlight_by_id(db, highlight_id)
    if not hl:
        raise HTTPException(status_code=404, detail="Highlight not found")
    if hl.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this highlight")
    hl = await story_crud.update_highlight(db, highlight_id, hl_data.title, hl_data.cover_url)
    return highlight_to_dict(hl)


@UserProtectedRouter.delete("/highlights/{highlight_id}")
async def delete_highlight(highlight_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    hl = await story_crud.get_highlight_by_id(db, highlight_id)
    if not hl:
        raise HTTPException(status_code=404, detail="Highlight not found")
    if hl.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this highlight")
    deleted = await story_crud.delete_highlight(db, highlight_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Highlight not found")
    return {"message": "Highlight deleted successfully"}


@UserProtectedRouter.post("/highlights/{highlight_id}/stories/{story_id}", status_code=201)
async def add_story_to_highlight(highlight_id: int, story_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    hl = await story_crud.get_highlight_by_id(db, highlight_id)
    story = await story_crud.get_story_by_id(db, story_id)
    if not hl or not story:
        raise HTTPException(status_code=404, detail="Highlight or Story not found")
    if hl.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to add stories to this highlight")
    await story_crud.add_story_to_highlight(db, highlight_id, story_id)
    return {"message": "Story added to highlight successfully"}


@UserProtectedRouter.delete("/highlights/{highlight_id}/stories/{story_id}")
async def remove_story_from_highlight(highlight_id: int, story_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    hl = await story_crud.get_highlight_by_id(db, highlight_id)
    if not hl:
        raise HTTPException(status_code=404, detail="Highlight not found")
    if hl.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to remove stories from this highlight")
    removed = await story_crud.remove_story_from_highlight(db, highlight_id, story_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Highlight story association not found")
    return {"message": "Story removed from highlight successfully"}


@UserProtectedRouter.get("/highlights/{highlight_id}/stories")
async def get_stories_in_highlight(highlight_id: int, db: AsyncSession = Depends(get_db)):
    hl = await story_crud.get_highlight_by_id(db, highlight_id)
    if not hl:
        raise HTTPException(status_code=404, detail="Highlight not found")
    stories = await story_crud.get_stories_in_highlight(db, highlight_id)
    return [story_to_dict(s) for s in stories]


@UserRouter.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    UPLOAD_DIR = "static/uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mov", ".avi", ".mkv"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only standard images and videos are allowed.")
    
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"url": f"/static/uploads/{unique_filename}"}


@UserProtectedRouter.post("/reels", status_code=201)
async def create_new_reel(reel_data: reel_schemas.ReelCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    reel = await reel_crud.create_reel(
        db=db,
        user_id=current_user.user_id,
        video_url=reel_data.video_url,
        caption=reel_data.caption
    )
    return reel_to_dict(reel)


@UserProtectedRouter.get("/reels")
async def get_all_reels_endpoint(db: AsyncSession = Depends(get_db)):
    reels = await reel_crud.get_all_reels(db)
    return [reel_to_dict(r) for r in reels]


@UserProtectedRouter.get("/users/{user_id}/reels")
async def get_user_reels_endpoint(user_id: int, db: AsyncSession = Depends(get_db)):
    reels = await reel_crud.get_reels_by_user(db, user_id)
    return [reel_to_dict(r) for r in reels]


@UserProtectedRouter.delete("/reels/{reel_id}")
async def delete_reel_endpoint(reel_id: int, db: AsyncSession = Depends(get_db), mongo_db = Depends(get_mongo_db), current_user = Depends(get_current_user)):
    reel = await reel_crud.get_reel_by_id(db, reel_id)
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")
    admin_check = await db.execute(
        select(Role)
        .join(UserRole, Role.role_id == UserRole.role_id)
        .where(UserRole.user_id == current_user.user_id, Role.role_name == "Admin")
    )
    is_admin = admin_check.scalar_one_or_none() is not None
    if reel.user_id != current_user.user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this reel")
        
    deleted = await reel_crud.delete_reel(db, reel_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Reel not found")
        
    await mongo_db.reel_likes.delete_many({"reel_id": reel_id})
    return {"message": "Reel and likes deleted successfully"}


@UserProtectedRouter.post("/reels/{reel_id}/like", status_code=201)
async def like_reel_endpoint(reel_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user), mongo_db = Depends(get_mongo_db)):
    reel = await reel_crud.get_reel_by_id(db, reel_id)
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")
        
    from datetime import datetime
    like_doc = {
        "reel_id": reel_id,
        "user_id": current_user.user_id,
        "created_at": datetime.utcnow().isoformat()
    }
    try:
        await mongo_db.reel_likes.insert_one(like_doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Reel already liked")
        
    return {"message": "Reel liked successfully"}


@UserProtectedRouter.delete("/reels/{reel_id}/like/{user_id}")
async def unlike_reel_endpoint(reel_id: int, user_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user), mongo_db = Depends(get_mongo_db)):
    reel = await reel_crud.get_reel_by_id(db, reel_id)
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")
        
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")
        
    result = await mongo_db.reel_likes.delete_one({"reel_id": reel_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Like not found")
        
    return {"message": "Reel unliked successfully"}


@UserProtectedRouter.get("/reels/{reel_id}/likes/count")
async def get_reel_likes_count_endpoint(reel_id: int, db: AsyncSession = Depends(get_db), mongo_db = Depends(get_mongo_db)):
    reel = await reel_crud.get_reel_by_id(db, reel_id)
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")
        
    count = await mongo_db.reel_likes.count_documents({"reel_id": reel_id})
    return {"likes_count": count}


@UserProtectedRouter.get("/reels/{reel_id}/likes/users")
async def get_users_who_liked_reel(reel_id: int, db: AsyncSession = Depends(get_db), mongo_db = Depends(get_mongo_db)):
    reel = await reel_crud.get_reel_by_id(db, reel_id)
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")
        
    cursor = mongo_db.reel_likes.find({"reel_id": reel_id})
    likes = await cursor.to_list(length=1000)
    user_ids = [l["user_id"] for l in likes]
    
    users = []
    if user_ids:
        for u_id in user_ids:
            user = await user_crud.get_user_by_id(db, u_id)
            if user:
                users.append(user_to_dict(user))
                
    return users

