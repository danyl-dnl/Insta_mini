import asyncio
from sqlalchemy import select
from Setting.Database import SessionLocal
from Setting.Models import Role

async def seed_roles():
    target_roles = ["Admin", "Supervisor", "User","SuperAdmin"]

    async with SessionLocal() as session:
        for role_name in target_roles:
            result = await session.execute(select(Role).where(Role.role_name == role_name))

            role_record = result.scalar_one_or_none()

            if not role_record:
                print(f"Role {role_name} not found")

                new_role = Role(role_name=role_name)

                session.add(new_role)
            else:
                print(f"Role {role_name} already exists")
            
            print("Database seeding completed")

        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed_roles())

            
        

