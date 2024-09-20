import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base


class Post(Base):
    __tablename__ = "Posts"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    content = Column(String)
    upvotes = Column(Integer, default=0)
    author = Column(String, default="Anonymous")
    category = Column(String, default="Carrier Comparison")
    created_at = Column(DateTime, default=datetime.utcnow())

    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan", lazy='joined')

class Comment(Base):
    __tablename__ = "Comments"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    content = Column(String)
    upvotes = Column(Integer, default=0)
    author = Column(String, default="Anonymous")
    created_at = Column(DateTime, default=datetime.utcnow())

    post_id = Column(String, ForeignKey("Posts.id"))
    post = relationship("Post", back_populates="comments")