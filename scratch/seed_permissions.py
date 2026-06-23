import sys
import os
import asyncio

# Setup path so the VS Code Run Button works
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from Setting.Database import SessionLocal
from Setting.Models import Feature, Action, FeatureAction, Role, RoleFeatureAction

async def seed_permissions():
    async with SessionLocal() as session:
        features_to_seed = ["post", "comment", "reel", "user", "role"]
        feature_map = {}

        for fname in features_to_seed:
            result = await session.execute(select(Feature).where(Feature.feature_name == fname))
            feature = result.scalar_one_or_none()
            if not feature:
                feature = Feature(feature_name=fname)
                session.add(feature)
                await session.flush()  # flushes so database generates feature_id immediately
            feature_map[fname] = feature


        actions_to_seed = ["create", "view", "update", "delete"]
        action_map={}

        for aname in actions_to_seed:
            exist = await session.execute(select(Action).where(Action.action_name==aname))
            result = exist.scalar_one_or_none()
            if not result:
                result = Action(action_name=aname)
                session.add(result)
                await session.flush()
            action_map[aname] = result
        
        

        feature_action_map = {}
        for fname, feature_obj in feature_map.items():
            for aname, action_obj in action_map.items():
                result = await session.execute(
                    select(FeatureAction).where(
                        FeatureAction.feature_id == feature_obj.feature_id,
                        FeatureAction.action_id == action_obj.action_id
                    )
                )
                fa = result.scalar_one_or_none()
                if not fa:
                    fa = FeatureAction(
                        feature_id=feature_obj.feature_id,
                        action_id=action_obj.action_id,
                        permission_name=f"{fname}:{aname}"
                    )
                    session.add(fa)
                    await session.flush()
                feature_action_map[f"{fname}:{aname}"] = fa

        
        
        role_permissions_definition = {
            "User": [
                "post:create", "post:view", "post:update", "post:delete",
                "comment:create", "comment:view", "comment:update", "comment:delete",
                "reel:create", "reel:view", "reel:update", "reel:delete"
            ],
            "Supervisor": [
                "post:create", "post:view", "post:update", "post:delete",
                "comment:create", "comment:view", "comment:update", "comment:delete",
                "reel:create", "reel:view", "reel:update", "reel:delete",
                "post:delete", "comment:delete", "reel:delete"
            ],
            "Admin": [
                "post:create", "post:view", "post:update", "post:delete",
                "comment:create", "comment:view", "comment:update", "comment:delete",
                "reel:create", "reel:view", "reel:update", "reel:delete",
                "user:view", "user:delete", "role:update"
            ],
            "SuperAdmin": [
                f"{f}:{a}" for f in features_to_seed for a in actions_to_seed
            ]
        }


        for role_name, permission_keys in role_permissions_definition.items():
            role_result = await session.execute(select(Role).where(Role.role_name == role_name))
            role_obj = role_result.scalar_one_or_none()

            if not role_obj:
                print(f"Role '{role_name}' not found. Please run seed_roles.py first!")
                continue
            
            for key in permission_keys:
                fa_obj = feature_action_map.get(key)
                if fa_obj:
                    link_result = await session.execute(
                        select(RoleFeatureAction).where(
                            RoleFeatureAction.role_id == role_obj.role_id,
                            RoleFeatureAction.feature_action_id == fa_obj.feature_action_id
                        )
                    )
                    link = link_result.scalar_one_or_none()
                    if not link:
                        link = RoleFeatureAction(
                            role_id=role_obj.role_id,
                            feature_action_id=fa_obj.feature_action_id
                        )
                        session.add(link)
        
        await session.commit()
    print("Database permissions seeded successfully!")
if __name__ == "__main__":
    asyncio.run(seed_permissions())
