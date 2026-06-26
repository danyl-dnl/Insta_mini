from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from Setting.Database import get_db
from Setting.Models import Role, UserRole
from Setting.Mongo import get_mongo_db
from User.Router import get_current_user, PermissionChecker
import Admin.CRUD.role as role_crud
import Admin.CRUD.user as user_crud
import Admin.CRUD.post as post_crud
import Admin.Schemas.role as schemas

AdminRouter = APIRouter()


def role_to_dict(role):
    if not role:
        return None
    return {"role_id": role.role_id, "role_name": role.role_name}


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


@AdminRouter.post("/roles", status_code=201)
async def create_role(
    role_data: schemas.RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(PermissionChecker("role", "create")),
):
    existing = await role_crud.get_role_by_name(db, role_data.role_name)
    if existing:
        raise HTTPException(status_code=400, detail="Role name already exists")
    role = await role_crud.create_role(db, role_data.role_name)
    return role_to_dict(role)


@AdminRouter.get("/roles")
async def get_all_roles(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(PermissionChecker("role", "view")),
):
    roles = await role_crud.get_all_roles(db)
    return [role_to_dict(r) for r in roles]



@AdminRouter.get("/roles/{role_id}")
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(PermissionChecker("role", "view")),
):
    role = await role_crud.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role_to_dict(role)


@AdminRouter.get("/roles/name/{role_name}")
async def get_role_by_name(
    role_name: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(PermissionChecker("role", "view")),
):
    role = await role_crud.get_role_by_name(db, role_name)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role_to_dict(role)


@AdminRouter.put("/roles/{role_id}")
async def update_role(
    role_id: int,
    role_data: schemas.RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(PermissionChecker("role", "update")),
):
    role = await role_crud.update_role(db, role_id, role_data.role_name)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role_to_dict(role)


@AdminRouter.delete("/roles/{role_id}")
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(PermissionChecker("role", "delete")),
):
    deleted = await role_crud.delete_role(db, role_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Role deleted successfully"}


@AdminRouter.get("/users")
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(PermissionChecker("user", "view")),
):
    users = await user_crud.get_all_users(db)
    return [user_to_dict(u) for u in users]


@AdminRouter.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
    current_user=Depends(PermissionChecker("user", "delete")),
):
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    reel_ids = [reel.reel_id for reel in user.reels] if user.reels else []
    
    deleted = await user_crud.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
        
    await mongo_db.reel_likes.delete_many({"user_id": user_id})
    if reel_ids:
        await mongo_db.reel_likes.delete_many({"reel_id": {"$in": reel_ids}})
        
    return {"message": "User and all associated data deleted successfully"}


@AdminRouter.get("/posts")
async def get_all_posts(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(PermissionChecker("post", "view")),
):
    posts = await post_crud.get_all_posts(db)
    return [post_to_dict(p) for p in posts]


@AdminRouter.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(PermissionChecker("post", "delete")),
):
    deleted = await post_crud.delete_post(db, post_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post and associated likes/comments deleted successfully"}
