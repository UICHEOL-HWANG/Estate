from sqlalchemy import Column, Integer, UniqueConstraint
from .database import Base

class PostLike(Base):
    __tablename__ = "post_likes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, nullable=False)  # ✅ 게시글 ID (board_service에서 제공)
    user_id = Column(Integer, nullable=False)  # ✅ Django의 회원 ID

    __table_args__ = (UniqueConstraint("post_id", "user_id", name="unique_post_like"),)

class CommentLike(Base):
    __tablename__ = "comment_likes"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, nullable=False)  # ✅ 댓글 ID (board_service에서 제공)
    user_id = Column(Integer, nullable=False)  # ✅ Django의 회원 ID

    __table_args__ = (UniqueConstraint("comment_id", "user_id", name="unique_comment_like"),)
