from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from model.database import get_db

from dto.post import PostCreate

router = APIRouter()

@router.post("/")
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    new_post = Post(title=post.title, content=post.content, author_id=post.author_id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

