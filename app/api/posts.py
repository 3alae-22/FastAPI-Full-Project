from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import models
from app.database.database import get_db
from app.models.schemas import PostCreate, PostResponse



router = APIRouter(
    prefix="/api/posts",
    tags=["posts"],
)


@router.get(
    "",
    response_model=list[PostResponse],
)
def get_posts(
    db: Annotated[Session, Depends(get_db)],
):

    result = db.execute(
        select(models.Post)
    )

    posts = result.scalars().all()

    return posts


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post(
    post: PostCreate,
    db: Annotated[Session, Depends(get_db)],
):

    result = db.execute(
        select(models.User).where(
            models.User.id == post.user_id
        )
    )

    user = result.scalars().first()

    if not user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
    )

    db.add(new_post)

    db.commit()

    db.refresh(new_post)

    return new_post


@router.get(
    "/{post_id}",
    response_model=PostResponse,
)
def get_post(
    post_id: int,
    db: Annotated[Session, Depends(get_db)],
):

    result = db.execute(
        select(models.Post).where(
            models.Post.id == post_id
        )
    )

    post = result.scalars().first()

    if post:

        return post

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Post not found",
    )