from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, nullable=False)  # Django 회원 ID
    created_at = Column(DateTime, default=func.now())

    comments = relationship("Comment", back_populates="post", cascade="all, delete")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, nullable=False)  # Django 회원 ID
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    post = relationship("Post", back_populates="comments")