from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.api import pages, users, posts, errors
from app.database.database import Base, engine


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/media", StaticFiles(directory="../media"), name="media")


app.include_router(pages.router)

app.include_router(users.router)

app.include_router(posts.router)

errors.register_exception_handlers(app)