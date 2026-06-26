import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Setting.Database import SessionLocal
from Setting.Models import (
    User,
    UserRole,
    Post,
    PostComment,
    PostLike,
    SavedPost,
    Reel,
    Story,
    Highlight,
    HighlightStory,
    UserFollower,
    CloseFriend,
    UserBio,
    PrivacyHistory,
    RefreshToken,
)


async def clear_all_users():
    async with SessionLocal() as session:
        print("🧹 Clearing all user-related data from the database...")

        # Delete dependent tables first to avoid foreign key conflicts
        await session.execute(RefreshToken.__table__.delete())
        await session.execute(PrivacyHistory.__table__.delete())
        await session.execute(UserBio.__table__.delete())
        await session.execute(HighlightStory.__table__.delete())
        await session.execute(Highlight.__table__.delete())
        await session.execute(Story.__table__.delete())
        await session.execute(Reel.__table__.delete())
        await session.execute(SavedPost.__table__.delete())
        await session.execute(PostLike.__table__.delete())
        await session.execute(PostComment.__table__.delete())
        await session.execute(Post.__table__.delete())
        await session.execute(UserRole.__table__.delete())
        await session.execute(UserFollower.__table__.delete())
        await session.execute(CloseFriend.__table__.delete())

        # Finally delete users
        await session.execute(User.__table__.delete())

        await session.commit()
    print(
        "✨ All user accounts and their associated data have been successfully deleted!"
    )


if __name__ == "__main__":
    asyncio.run(clear_all_users())
