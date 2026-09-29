from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import models
from app.database.database import get_db
from app.models.schemas import PostResponse,UserCreate,UserResponse,Useruser_data



router = APIRouter(
    prefix="/api/users",
    tags=["users"],
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user: UserCreate,
    db: Annotated[Session, Depends(get_db)],
):

    result = db.execute(
        select(models.User).where(
            models.User.username == user.username
        ),
    )

    existing_user = result.scalars().first()

    if existing_user:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    result = db.execute(
        select(models.User).where(
            models.User.email == user.email
        ),
    )

    existing_email = result.scalars().first()

    if existing_email:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = models.User(
        username=user.username,
        email=user.email,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):

    result = db.execute(
        select(models.User).where(
            models.User.id == user_id
        ),
    )
    user = result.scalars().first()
    if user:
        return user

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",
    )


@router.get(
    "/{user_id}/posts",
    response_model=list[PostResponse],
)
def get_user_posts(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(
        select(models.User).where(
            models.User.id == user_id
        )
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = db.execute(
        select(models.Post).where(
            models.Post.user_id == user_id
        )
    )
    posts = result.scalars().all()

    return posts

@router.patch(
    "/{user_id}/posts",
    response_model=list[PostResponse],
)
def user_data_user_posts(
    user_id: int,
    user_data: UserCreate,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(
        select(models.User).where(
            models.User.id == user_id
        )
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user_data.username is not None and user_data.username != user.username:
        result = db.execute(
            select(models.User).where(
                models.User.user_name == user_data.username
            )
        )
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

    if user_data.email is not None and user_data.email != user.email:
        result = db.execute(
            select(models.User).where(
                models.User.email == user_data.email
            )
        )
        existing_email = result.scalars().first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

    if user_data.username is not None:
        user.username = user_data.username
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.image_file is not None:
        user.image_file = user_data.image_file

    db.commit()
    db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(
            models.User.id == user_id
        )
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db.delete(user)
    db.commit()


    












