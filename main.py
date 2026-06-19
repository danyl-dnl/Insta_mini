from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import crud
import schemas

app = FastAPI(title="Instagram Backend API")

# Enable CORS for frontend API calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


def follow_to_dict(follow):
    if not follow:
        return None
    return {
        "follow_id": follow.follow_id,
        "follower_id": follow.follower_id,
        "following_id": follow.following_id,
        "is_active": follow.is_active,
        "created_at": follow.created_at.isoformat() if follow.created_at else None,
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


def like_to_dict(like):
    if not like:
        return None
    return {
        "like_id": like.like_id,
        "user_id": like.user_id,
        "post_id": like.post_id,
        "created_at": like.created_at.isoformat() if like.created_at else None,
    }


@app.get("/")
async def root():
    return {"message": "Welcome to the Instagram Backend API! Visit /docs for interactive Swagger UI."}

# role

@app.post("/roles", status_code=201)
async def create_role(role_data: schemas.RoleCreate):
    existing = await crud.get_role_by_name(role_data.role_name)
    if existing:
        raise HTTPException(status_code=400, detail="Role name already exists")
    role = await crud.create_role(role_data.role_name)
    return role_to_dict(role)


@app.get("/roles/{role_id}")
async def get_role(role_id: int):
    role = await crud.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role_to_dict(role)


@app.get("/roles/name/{role_name}")
async def get_role_by_name(role_name: str):
    role = await crud.get_role_by_name(role_name)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role_to_dict(role)


@app.put("/roles/{role_id}")
async def update_role(role_id: int, role_data: schemas.RoleUpdate):
    role = await crud.update_role(role_id, role_data.role_name)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role_to_dict(role)


@app.delete("/roles/{role_id}")
async def delete_role(role_id: int):
    deleted = await crud.delete_role(role_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Role deleted successfully"}


#  Users 

@app.post("/users", status_code=201)
async def create_user(user_data: schemas.UserCreate):
    existing_username = await crud.get_user_by_username(user_data.username)
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    existing_email = await crud.get_user_by_email(user_data.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = await crud.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        profile_picture=user_data.profile_picture
    )
    return user_to_dict(user)


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_to_dict(user)


@app.get("/users/username/{username}")
async def get_user_by_username(username: str):
    user = await crud.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_to_dict(user)


@app.get("/users/email/{email}")
async def get_user_by_email(email: str):
    user = await crud.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_to_dict(user)

 
@app.put("/users/{user_id}")
async def update_user(user_id: int, user_data: schemas.UserUpdate):
    user = await crud.update_user(
        user_id=user_id,
        full_name=user_data.full_name,
        profile_picture=user_data.profile_picture
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_to_dict(user)


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    deleted = await crud.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User and all associated data deleted successfully"}


# User Bio

@app.post("/users/{user_id}/bio", status_code=201)
async def create_user_bio(user_id: int, bio_data: schemas.UserBioCreate):
    user = await crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    bio = await crud.create_user_bio(user_id, bio_data.bio_text, bio_data.is_active)
    return bio_to_dict(bio)


@app.get("/users/{user_id}/bio")
async def get_active_bio(user_id: int):
    user = await crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    bio = await crud.get_active_user_bio(user_id)
    if not bio:
        raise HTTPException(status_code=404, detail="Active bio not found for user")
    return bio_to_dict(bio)


@app.put("/bios/{bio_id}")
async def update_bio(bio_id: int, bio_data: schemas.UserBioUpdate):
    bio = await crud.update_user_bio(bio_id, bio_data.bio_text, bio_data.is_active)
    if not bio:
        raise HTTPException(status_code=404, detail="Bio not found")
    return bio_to_dict(bio)


@app.delete("/bios/{bio_id}")
async def delete_bio(bio_id: int):
    deleted = await crud.delete_user_bio(bio_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Bio not found")
    return {"message": "Bio deleted successfully"}


@app.post("/users/{user_id}/roles/{role_id}", status_code=201)
async def assign_role_to_user(user_id: int, role_id: int):
    user = await crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    role = await crud.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    await crud.assign_role_to_user(user_id, role_id)
    return {"message": "Role assigned successfully"}


@app.get("/users/{user_id}/roles")
async def get_user_roles(user_id: int):
    user = await crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    roles = await crud.get_user_roles(user_id)
    return [role_to_dict(r) for r in roles]


@app.delete("/users/{user_id}/roles/{role_id}")
async def remove_role_from_user(user_id: int, role_id: int):
    removed = await crud.remove_role_from_user(user_id, role_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Role assignment not found")
    return {"message": "Role removed successfully"}


# --- Privacy History Endpoints ---

@app.post("/users/{user_id}/privacy", status_code=201)
async def create_privacy_setting(user_id: int, privacy_data: schemas.PrivacyHistoryCreate):
    user = await crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    ph = await crud.create_privacy_history(user_id, privacy_data.privacy_type, privacy_data.is_active)
    return privacy_to_dict(ph)


@app.get("/users/{user_id}/privacy")
async def get_active_privacy(user_id: int):
    user = await crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    settings = await crud.get_active_privacy_settings(user_id)
    return [privacy_to_dict(ph) for ph in settings]


@app.put("/privacy/{privacy_id}")
async def update_privacy(privacy_id: int, privacy_data: schemas.PrivacyHistoryUpdate):
    ph = await crud.update_privacy_setting(privacy_id, privacy_data.is_active)
    if not ph:
        raise HTTPException(status_code=404, detail="Privacy record not found")
    return privacy_to_dict(ph)


@app.delete("/privacy/{privacy_id}")
async def delete_privacy(privacy_id: int):
    deleted = await crud.delete_privacy_history(privacy_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Privacy record not found")
    return {"message": "Privacy record deleted successfully"}


# Posts 

@app.post("/posts", status_code=201)
async def create_post(post_data: schemas.PostCreate):
    user = await crud.get_user_by_id(post_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    post = await crud.create_post(post_data.user_id, post_data.caption, post_data.image_url)
    return post_to_dict(post)


@app.get("/posts/{post_id}")
async def get_post(post_id: int):
    post = await crud.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post_to_dict(post)


@app.get("/users/{user_id}/posts")
async def get_user_posts(user_id: int):
    user = await crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    posts = await crud.get_posts_by_user(user_id)
    return [post_to_dict(p) for p in posts]


@app.put("/posts/{post_id}")
async def update_post(post_id: int, post_data: schemas.PostUpdate):
    post = await crud.update_post(post_id, post_data.caption)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post_to_dict(post)


@app.delete("/posts/{post_id}")
async def delete_post(post_id: int):
    deleted = await crud.delete_post(post_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post and associated likes/comments deleted successfully"}


# Follows

@app.post("/users/{follower_id}/follow/{following_id}", status_code=201)
async def follow_user(follower_id: int, following_id: int):
    if follower_id == following_id:
        raise HTTPException(status_code=400, detail="Users cannot follow themselves")
    follower = await crud.get_user_by_id(follower_id)
    following = await crud.get_user_by_id(following_id)
    if not follower or not following:
        raise HTTPException(status_code=404, detail="Follower or following user not found")
    record = await crud.follow_user(follower_id, following_id)
    return follow_to_dict(record)


@app.post("/users/{follower_id}/unfollow/{following_id}")
async def unfollow_user(follower_id: int, following_id: int):
    unfollowed = await crud.unfollow_user(follower_id, following_id)
    if not unfollowed:
        raise HTTPException(status_code=404, detail="Follow relationship not found")
    return follow_to_dict(unfollowed)


@app.get("/users/{user_id}/followers")
async def get_followers(user_id: int):
    user = await crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    followers = await crud.get_followers(user_id)
    return [user_to_dict(f) for f in followers]


@app.get("/users/{user_id}/following")
async def get_following(user_id: int):
    user = await crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    following = await crud.get_following(user_id)
    return [user_to_dict(f) for f in following]


# Stories 

@app.post("/stories", status_code=201)
async def create_story(story_data: schemas.StoryCreate):
    user = await crud.get_user_by_id(story_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    story = await crud.create_story(story_data.user_id, story_data.media_url)
    return story_to_dict(story)


@app.get("/users/{user_id}/stories/active")
async def get_active_stories(user_id: int):
    user = await crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    stories = await crud.get_active_stories_by_user(user_id)
    return [story_to_dict(s) for s in stories]


@app.delete("/stories/{story_id}")
async def delete_story(story_id: int):
    deleted = await crud.delete_story(story_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Story not found")
    return {"message": "Story deleted successfully"}


# Saved Posts 

@app.post("/users/{user_id}/save/{post_id}", status_code=201)
async def save_post(user_id: int, post_id: int):
    user = await crud.get_user_by_id(user_id)
    post = await crud.get_post_by_id(post_id)
    if not user or not post:
        raise HTTPException(status_code=404, detail="User or Post not found")
    record = await crud.save_post(user_id, post_id)
    if not record:
        return {"message": "Post already saved"}
    return {"message": "Post saved successfully"}


@app.delete("/users/{user_id}/unsave/{post_id}")
async def unsave_post(user_id: int, post_id: int):
    deleted = await crud.unsave_post(user_id, post_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Saved post record not found")
    return {"message": "Post unsaved successfully"}


@app.get("/users/{user_id}/saved")
async def get_saved_posts(user_id: int):
    user = await crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    posts = await crud.get_saved_posts(user_id)
    return [post_to_dict(p) for p in posts]


# Highlights 

@app.post("/highlights", status_code=201)
async def create_highlight(hl_data: schemas.HighlightCreate):
    user = await crud.get_user_by_id(hl_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    hl = await crud.create_highlight(hl_data.user_id, hl_data.title, hl_data.cover_url)
    return highlight_to_dict(hl)


@app.get("/highlights/{highlight_id}")
async def get_highlight(highlight_id: int):
    hl = await crud.get_highlight_by_id(highlight_id)
    if not hl:
        raise HTTPException(status_code=404, detail="Highlight not found")
    return highlight_to_dict(hl)


@app.get("/users/{user_id}/highlights")
async def get_user_highlights(user_id: int):
    user = await crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    hls = await crud.get_highlights_by_user(user_id)
    return [highlight_to_dict(hl) for hl in hls]


@app.put("/highlights/{highlight_id}")
async def update_highlight(highlight_id: int, hl_data: schemas.HighlightUpdate):
    hl = await crud.update_highlight(highlight_id, hl_data.title, hl_data.cover_url)
    if not hl:
        raise HTTPException(status_code=404, detail="Highlight not found")
    return highlight_to_dict(hl)


@app.delete("/highlights/{highlight_id}")
async def delete_highlight(highlight_id: int):
    deleted = await crud.delete_highlight(highlight_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Highlight not found")
    return {"message": "Highlight deleted successfully"}


@app.post("/highlights/{highlight_id}/stories/{story_id}", status_code=201)
async def add_story_to_highlight(highlight_id: int, story_id: int):
    hl = await crud.get_highlight_by_id(highlight_id)
    story = await crud.get_story_by_id(story_id)
    if not hl or not story:
        raise HTTPException(status_code=404, detail="Highlight or Story not found")
    await crud.add_story_to_highlight(highlight_id, story_id)
    return {"message": "Story added to highlight successfully"}


@app.delete("/highlights/{highlight_id}/stories/{story_id}")
async def remove_story_from_highlight(highlight_id: int, story_id: int):
    removed = await crud.remove_story_from_highlight(highlight_id, story_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Highlight story association not found")
    return {"message": "Story removed from highlight successfully"}


@app.get("/highlights/{highlight_id}/stories")
async def get_stories_in_highlight(highlight_id: int):
    hl = await crud.get_highlight_by_id(highlight_id)
    if not hl:
        raise HTTPException(status_code=404, detail="Highlight not found")
    stories = await crud.get_stories_in_highlight(highlight_id)
    return [story_to_dict(s) for s in stories]


#  Close Friends

@app.post("/users/{user_id}/close-friends/{friend_id}", status_code=201)
async def add_close_friend(user_id: int, friend_id: int):
    if user_id == friend_id:
        raise HTTPException(status_code=400, detail="Cannot add yourself as close friend")
    user = await crud.get_user_by_id(user_id)
    friend = await crud.get_user_by_id(friend_id)
    if not user or not friend:
        raise HTTPException(status_code=404, detail="User or Friend not found")
    await crud.add_close_friend(user_id, friend_id)
    return {"message": "Added to close friends successfully"}


@app.delete("/users/{user_id}/close-friends/{friend_id}")
async def remove_close_friend(user_id: int, friend_id: int):
    removed = await crud.remove_close_friend(user_id, friend_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Close friend relationship not found")
    return {"message": "Removed from close friends successfully"}


@app.get("/users/{user_id}/close-friends")
async def get_close_friends(user_id: int):
    user = await crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    friends = await crud.get_close_friends(user_id)
    return [user_to_dict(f) for f in friends]


# Post Likes Endpoints

@app.post("/posts/{post_id}/like", status_code=201)
async def like_post(post_id: int, like_data: schemas.PostLikeCreate):
    post = await crud.get_post_by_id(post_id)
    user = await crud.get_user_by_id(like_data.user_id)
    if not post or not user:
        raise HTTPException(status_code=404, detail="Post or User not found")
    like = await crud.like_post(like_data.user_id, post_id)
    return like_to_dict(like)


@app.delete("/posts/{post_id}/like/{user_id}")
async def unlike_post(post_id: int, user_id: int):
    unliked = await crud.unlike_post(user_id, post_id)
    if not unliked:
        raise HTTPException(status_code=404, detail="Like record not found")
    return {"message": "Post unliked successfully"}


@app.get("/posts/{post_id}/likes/count")
async def get_post_likes_count(post_id: int):
    post = await crud.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    count = await crud.get_post_likes_count(post_id)
    return {"likes_count": count}


@app.get("/posts/{post_id}/likes/users")
async def get_users_who_liked_post(post_id: int):
    post = await crud.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    users = await crud.get_users_who_liked_post(post_id)
    return [user_to_dict(u) for u in users]


# Post Comments 

@app.post("/posts/{post_id}/comments", status_code=201)
async def add_comment(post_id: int, comment_data: schemas.CommentCreate):
    post = await crud.get_post_by_id(post_id)
    user = await crud.get_user_by_id(comment_data.user_id)
    if not post or not user:
        raise HTTPException(status_code=404, detail="Post or User not found")
    comment = await crud.add_comment(comment_data.user_id, post_id, comment_data.comment_text)
    return comment_to_dict(comment)


@app.get("/posts/{post_id}/comments")
async def get_comments_for_post(post_id: int):
    post = await crud.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comments = await crud.get_comments_for_post(post_id)
    return [comment_to_dict(c) for c in comments]


@app.get("/comments/{comment_id}")
async def get_comment(comment_id: int):
    comment = await crud.get_comment_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment_to_dict(comment)


@app.put("/comments/{comment_id}")
async def update_comment(comment_id: int, comment_data: schemas.CommentUpdate):
    comment = await crud.update_comment(comment_id, comment_data.comment_text)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment_to_dict(comment)


@app.delete("/comments/{comment_id}")
async def delete_comment(comment_id: int):
    deleted = await crud.delete_comment(comment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"message": "Comment deleted successfully"}


@app.get("/users")
async def get_all_users():
    users = await crud.get_all_users()
    return [user_to_dict(u) for u in users]


@app.get("/posts")
async def get_all_posts():
    posts = await crud.get_all_posts()
    return [post_to_dict(p) for p in posts]
