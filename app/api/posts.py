from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import models
from app.database.database import get_db
from app.models.schemas import PostCreate, PostResponse, PostUpdate



router = APIRouter(
    prefix="/api/posts",
    tags=["posts"],
)


@router.get("", response_model=list[PostResponse])
def get_posts(db: Annotated[Session, Depends(get_db)]):

    result = db.execute(
        select(models.Post)
    )
    posts = result.scalars().all()

    return posts


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED,
)
def create_post(post: PostCreate,db: Annotated[Session, Depends(get_db)]):

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


@router.get("/{post_id}",response_model=PostResponse)
def get_post(post_id: int, db: Annotated[Session, Depends(get_db)]):

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
        detail="Post not found"
    )

@router.put("/{post_id}",response_model=PostResponse)
def update_post_full(post_id: int, post_data: PostCreate, db: Annotated[Session, Depends(get_db)]):

    result = db.execute(
        select(models.Post).where(
            models.Post.id == post_id
        )
    )
    post = result.scalars().first()
    if  not post:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
        )
    if post_data.user_id != post.user_id:
        result = db.execute(select(models.User).where(models.User.id == post.user_id))
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
    post.title = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id

    db.commit()
    db.refresh(post)

    return post
            
@router.patch("/{post_id}",response_model=PostResponse)
def update_post_partial(post_id: int, post_data: PostUpdate, db: Annotated[Session, Depends(get_db)]):

    result = db.execute(
        select(models.Post).where(
            models.Post.id == post_id
        )
    )
    post = result.scalars().first()
    if  not post:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
        )
    update_data = post_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    db.commit()
    db.refresh(post)
    
    return post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.Post).where(
            models.Post.id == post_id
        )
    )
    post = result.scalars().first()
    if  not post:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
        )
    db.delete(post)
    db.commit()
            
    

