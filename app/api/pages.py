from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import models
from app.database.database import get_db


router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/", include_in_schema=False, name="home")
@router.get("/posts", include_in_schema=False, name="posts")
def home(request: Request, db: Annotated[Session, Depends(get_db)]):

    result = db.execute(select(models.Post))

    posts = result.scalars().all()

    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Home"},
    )


@router.get("/posts/{post_id}", include_in_schema=False)
def post_page(
    request: Request,
    post_id: int,
    db: Annotated[Session, Depends(get_db)],
):

    result = db.execute(
        select(models.Post).where(models.Post.id == post_id)
    )

    post = result.scalars().first()

    if post:

        title = post.title[:50]

        return templates.TemplateResponse(
            request,
            "post.html",
            {"post": post, "title": title},
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Post not found",
    )


@router.get(
    "/users/{user_id}/posts",
    include_in_schema=False,
    name="user_posts",
)
def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):

    result = db.execute(
        select(models.User).where(models.User.id == user_id)
    )

    user = result.scalars().first()

    if not user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = db.execute(
        select(models.Post).where(models.Post.user_id == user_id)
    )

    posts = result.scalars().all()

    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {
            "posts": posts,
            "user": user,
            "title": f"{user.username}'s Posts",
        },
    )