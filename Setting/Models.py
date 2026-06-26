from Setting.Database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship


class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True)
    role_name = Column(String(50), nullable=False, unique=True)

    user_roles = relationship("UserRole", back_populates="role", lazy="selectin")

    role_feature_actions = relationship(
        "RoleFeatureAction", back_populates="role", lazy="selectin"
    )


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    full_name = Column(String(150))
    profile_picture = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    bio = relationship("UserBio", back_populates="user", uselist=False, lazy="selectin")
    posts = relationship("Post", back_populates="author", lazy="selectin")
    stories = relationship("Story", back_populates="author", lazy="selectin")
    saved_posts = relationship("SavedPost", back_populates="user", lazy="selectin")
    highlights = relationship("Highlight", back_populates="user", lazy="selectin")
    user_roles = relationship("UserRole", back_populates="user", lazy="selectin")
    privacy_history = relationship(
        "PrivacyHistory", back_populates="user", lazy="selectin"
    )
    likes = relationship("PostLike", back_populates="user", lazy="selectin")
    comments = relationship("PostComment", back_populates="user", lazy="selectin")
    reels = relationship("Reel", back_populates="author", lazy="selectin")
    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", lazy="selectin"
    )


class UserBio(Base):
    __tablename__ = "user_bio"

    bio_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    bio_text = Column(Text)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "is_active",
            name="uq_user_bio_user_active",
            deferrable=True,
            initially="DEFERRED",
        ),
    )

    user = relationship("User", back_populates="bio")


class UserRole(Base):
    __tablename__ = "user_roles"

    user_role_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.role_id"), nullable=False)
    created_at = Column(DateTime)

    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")


class PrivacyHistory(Base):
    __tablename__ = "privacy_history"

    privacy_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    privacy_type = Column(String(20))
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "privacy_type",
            "is_active",
            name="uq_privacy_history",
            deferrable=True,
            initially="DEFERRED",
        ),
    )

    user = relationship("User", back_populates="privacy_history")


class Post(Base):
    __tablename__ = "post"

    post_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    caption = Column(Text)
    image_url = Column(String(255))
    created_at = Column(DateTime)

    author = relationship("User", back_populates="posts")
    likes = relationship("PostLike", back_populates="post", lazy="selectin")
    comments = relationship("PostComment", back_populates="post", lazy="selectin")
    saved_by = relationship("SavedPost", back_populates="post", lazy="selectin")


class UserFollower(Base):
    __tablename__ = "user_followers"

    follow_id = Column(Integer, primary_key=True)
    follower_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    following_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)

    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="uq_follow_pair"),
    )

    follower = relationship("User", foreign_keys=[follower_id], lazy="selectin")
    following = relationship("User", foreign_keys=[following_id], lazy="selectin")


class Story(Base):
    __tablename__ = "stories"

    story_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    media_url = Column(String(255))
    created_at = Column(DateTime)
    expires_at = Column(DateTime)

    author = relationship("User", back_populates="stories")
    highlight_stories = relationship(
        "HighlightStory", back_populates="story", lazy="selectin"
    )


class SavedPost(Base):
    __tablename__ = "saved_posts"

    saved_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    post_id = Column(Integer, ForeignKey("post.post_id"), nullable=False)
    created_at = Column(DateTime)

    __table_args__ = (UniqueConstraint("user_id", "post_id", name="uq_saved_post"),)

    user = relationship("User", back_populates="saved_posts")
    post = relationship("Post", back_populates="saved_by", lazy="selectin")


class Highlight(Base):
    __tablename__ = "highlights"

    highlight_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    title = Column(String(50), nullable=False)
    cover_url = Column(String(255))
    created_at = Column(DateTime)

    user = relationship("User", back_populates="highlights")
    highlight_stories = relationship(
        "HighlightStory", back_populates="highlight", lazy="selectin"
    )


class HighlightStory(Base):
    __tablename__ = "highlight_stories"

    highlight_id = Column(
        Integer, ForeignKey("highlights.highlight_id"), primary_key=True
    )
    story_id = Column(Integer, ForeignKey("stories.story_id"), primary_key=True)

    highlight = relationship("Highlight", back_populates="highlight_stories")
    story = relationship("Story", back_populates="highlight_stories")


class CloseFriend(Base):
    __tablename__ = "close_friends"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    friend_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)

    user = relationship("User", foreign_keys=[user_id], lazy="selectin")
    friend = relationship("User", foreign_keys=[friend_id], lazy="selectin")


class PostLike(Base):
    __tablename__ = "post_likes"

    like_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    post_id = Column(Integer, ForeignKey("post.post_id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (UniqueConstraint("user_id", "post_id", name="uq_post_like"),)

    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")


class PostComment(Base):
    __tablename__ = "post_comments"

    comment_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    post_id = Column(Integer, ForeignKey("post.post_id"), nullable=False)
    comment_text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")


class Reel(Base):
    __tablename__ = "reels"

    reel_id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    video_url = Column(String(255), nullable=False)
    caption = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    author = relationship("User", back_populates="reels")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token_id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="refresh_tokens")


class Feature(Base):
    __tablename__ = "features"

    feature_id = Column(Integer, primary_key=True)
    feature_name = Column(String(100), unique=True, nullable=False)

    feature_actions = relationship(
        "FeatureAction", back_populates="feature", lazy="selectin"
    )


class Action(Base):
    __tablename__ = "actions"

    action_id = Column(Integer, primary_key=True)
    action_name = Column(String(100), unique=True, nullable=False)
    feature_actions = relationship(
        "FeatureAction", back_populates="action", lazy="selectin"
    )


class FeatureAction(Base):
    __tablename__ = "feature_actions"

    feature_action_id = Column(Integer, primary_key=True)
    action_id = Column(Integer, ForeignKey("actions.action_id"), nullable=False)
    feature_id = Column(Integer, ForeignKey("features.feature_id"), nullable=False)
    permission_name = Column(String(150), unique=True, nullable=True)

    action = relationship("Action", back_populates="feature_actions")
    feature = relationship("Feature", back_populates="feature_actions")
    role_feature_actions = relationship(
        "RoleFeatureAction", back_populates="feature_action", lazy="selectin"
    )

    __table_args__ = (
        UniqueConstraint("feature_id", "action_id", name="uq_feature_action"),
    )


class RoleFeatureAction(Base):
    __tablename__ = "role_feature_actions"

    role_feature_action_id = Column(Integer, primary_key=True)
    role_id = Column(
        Integer, ForeignKey("roles.role_id", ondelete="CASCADE"), nullable=False
    )
    feature_action_id = Column(
        Integer,
        ForeignKey("feature_actions.feature_action_id", ondelete="CASCADE"),
        nullable=False,
    )

    role = relationship("Role", back_populates="role_feature_actions", lazy="selectin")
    feature_action = relationship(
        "FeatureAction", back_populates="role_feature_actions", lazy="selectin"
    )

    __table_args__ = (
        UniqueConstraint("role_id", "feature_action_id", name="uq_role_feature_action"),
    )
