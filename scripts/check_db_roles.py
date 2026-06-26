import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from Setting.Database import SessionLocal
from Setting.Models import User, UserRole, Role


async def check_roles():
    async with SessionLocal() as session:
        # Check all roles
        result_roles = await session.execute(select(Role))
        roles = result_roles.scalars().all()
        print("--- ROLES IN DATABASE ---")
        for r in roles:
            print(f"Role ID: {r.role_id} | Name: {r.role_name}")
        print()

        # Check users and their roles
        query = (
            select(User.username, Role.role_name)
            .join(UserRole, User.user_id == UserRole.user_id)
            .join(Role, UserRole.role_id == Role.role_id)
        )
        result = await session.execute(query)
        mappings = result.all()

        print("--- USER ROLE ASSIGNMENTS ---")
        if not mappings:
            print("No users have any roles assigned yet!")
        else:
            for username, role_name in mappings:
                print(f"User: @{username} ---> Role: {role_name}")
        print()

        # Check users without roles
        all_users_result = await session.execute(select(User))
        all_users = all_users_result.scalars().all()
        assigned_usernames = {m[0] for m in mappings}
        unassigned = [
            u.username for u in all_users if u.username not in assigned_usernames
        ]

        if unassigned:
            print("--- USERS WITH NO ROLES ---")
            for u in unassigned:
                print(f"User: @{u}")


if __name__ == "__main__":
    asyncio.run(check_roles())
