from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import pages, users, posts, errors
from app.database.database import Base, engine


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/media", StaticFiles(directory="../media"), name="media")


app.include_router(pages.router)

app.include_router(users.router)

app.include_router(posts.router)

errors.register_exception_handlers(app)